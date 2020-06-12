#define KBUILD_MODNAME "tcpcctrace"
#include <uapi/linux/ptrace.h>
#include <uapi/linux/tcp.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <net/tcp.h>
#include <linux/kernel.h>


#define MIN(a,b) ((a) < (b) ? (a) : (b))

//__u32   be32_to_cpu(const __be32);

/* BIC TCP Parameters */
struct bictcp {
	u32	cnt;		/* increase cwnd by 1 after ACKs */
	u32	last_max_cwnd;	/* last maximum snd_cwnd */
	u32	last_cwnd;	/* the last snd_cwnd */
	u32	last_time;	/* time when updated last_cwnd */
	u32	bic_origin_point;/* origin point of bic function */
	u32	bic_K;		/* time to origin point
				   from the beginning of the current epoch */
	u32	delay_min;	/* min delay (msec << 3) */
	u32	epoch_start;	/* beginning of an epoch */
	u32	ack_cnt;	/* number of acks */
	u32	tcp_cwnd;	/* estimated tcp cwnd */
	u16	unused;
	u8	sample_cnt;	/* number of samples to decide curr_rtt */
	u8	found;		/* the exit point is found? */
	u32	round_start;	/* beginning of each round */
	u32	end_seq;	/* end_seq of the round */
	u32	last_ack;	/* last time when the ACK spacing is close */
	u32	curr_rtt;	/* the minimum rtt of current round */
};

struct cwnd_info {
	u32 saddr;
    u64 timestamp;
	u32 snd_cwnd;
	u32 pkts_in_flight;
	u32 min_rtt;
	u32 smoothed_rtt;
	u32 latest_rtt;
	u32 rttvar_us;
};

struct init_info {
	u32 saddr;
    u64 timestamp;
	u32 round_start;
	u32 end_seq;
	u32 curr_rtt;
	u8 sample_cnt;
	u32 ssthresh;
	u32 mdev_us;
	u32 icsk_rto;
};

struct pkt_lost {
	u32 saddr;
    u64 timestamp;
	int loss_trigger;
	u32 seq;
};

struct timer_info {
	u32 saddr;
    u64 timestamp;
	int type;
	u32 timer;
};


// eBPF tables to output data
BPF_PERF_OUTPUT(cwnd_change);
BPF_PERF_OUTPUT(init_event);
BPF_PERF_OUTPUT(mark_lost);
BPF_PERF_OUTPUT(timer_calc);

static unsigned int jiffiestousecs(const unsigned long j)
{
	/*
	 * Hz usually doesn't go much further MSEC_PER_SEC.
	 * jiffies_to_usecs() and usecs_to_jiffies() depend on that.
	 */
	//BUILD_BUG_ON(HZ > USEC_PER_SEC);

#if !(USEC_PER_SEC % HZ)
	return (USEC_PER_SEC / HZ) * j;
#else
# if BITS_PER_LONG == 32
	return (HZ_TO_USEC_MUL32 * j) >> HZ_TO_USEC_SHR32;
# else
	return (j * HZ_TO_USEC_NUM) / HZ_TO_USEC_DEN;
# endif
#endif
}

// Trace CWND changes during congestion avoidance
void trace_cong_avoid(struct pt_regs *ctx, struct tcp_sock *tp, u32 w, u32 acked) {
	const struct sock *sk = &(tp->inet_conn.icsk_inet.sk);
	u16 family = sk->__sk_common.skc_family;
	
	if (family == AF_INET) {
		struct cwnd_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;

		info.min_rtt = tp->rtt_min.s[0].v;
		info.smoothed_rtt = tp->srtt_us >> 3;
		info.latest_rtt = tp->rack.rtt_us;
		info.rttvar_us = tp->rttvar_us;
		info.snd_cwnd = tp->snd_cwnd;
		info.pkts_in_flight = tp->packets_out;
		
		cwnd_change.perf_submit(ctx, &info, sizeof(info));

		const struct inet_connection_sock *icsk = inet_csk(sk);
		struct timer_info info2 = {};
		info2.timestamp = info.timestamp;
		info2.saddr = info.saddr;
		
		info2.type = 3;
		info2.timer = jiffiestousecs(icsk->icsk_rto);

		timer_calc.perf_submit(ctx, &info2, sizeof(info2));
	}
}

// Trace CWND changes during slow start
void trace_slow_start(struct pt_regs *ctx, struct tcp_sock *tp, u32 acked) {
	const struct sock *sk = &(tp->inet_conn.icsk_inet.sk);
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct cwnd_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;

		info.snd_cwnd = tp->snd_cwnd;
		info.min_rtt = tp->rtt_min.s[0].v;
		info.smoothed_rtt = tp->srtt_us >> 3;
		info.latest_rtt = tp->rack.rtt_us;
		info.rttvar_us = tp->rttvar_us;
		
		if (acked <= tp->packets_out)
			info.pkts_in_flight = tp->packets_out - acked;
		else
			info.pkts_in_flight = 0;
		cwnd_change.perf_submit(ctx, &info, sizeof(info));
	}
}

// Trace init congestion control
void trace_init_cong_control(struct pt_regs *ctx, struct sock *sk) {
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct init_info info = {};
		info.timestamp = bpf_ktime_get_ns();

		const struct tcp_sock *tp = tcp_sk(sk);
		const struct bictcp *ca = inet_csk_ca(sk);
		const struct inet_connection_sock *icsk = inet_csk(sk);

		info.saddr = sk->__sk_common.skc_rcv_saddr;
		info.round_start = ca->round_start;
		info.end_seq = ca->end_seq;
		info.curr_rtt = ca->curr_rtt;
		info.sample_cnt = ca->sample_cnt;
		info.ssthresh = tp->snd_ssthresh;
		info.mdev_us = tp->mdev_us;
		info.icsk_rto = icsk->icsk_rto;
		

		init_event.perf_submit(ctx, &info, sizeof(info));
	}
}

static struct tcphdr *skb_to_tcphdr(const struct sk_buff *skb)
{
    // unstable API. verify logic in tcp_hdr() -> skb_transport_header().
    return (struct tcphdr *)(skb->head + skb->transport_header);
}

// Trace packets marked as lost
void trace_mark_lost(struct pt_regs *ctx, struct sock *sk, struct sk_buff *skb){
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct pkt_lost info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;

		struct tcphdr *tcp = skb_to_tcphdr(skb);
		info.loss_trigger = 1;
		info.seq = tcp->seq;
		info.seq = be32_to_cpu(info.seq);

		mark_lost.perf_submit(ctx, &info, sizeof(info));
	}
}

void trace_timeout_trigger(struct pt_regs *ctx, struct sock *sk) {
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct pkt_lost info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;

		const struct inet_connection_sock *icsk = inet_csk(sk);
		int event = icsk->icsk_pending;
		switch (event) {
		case ICSK_TIME_LOSS_PROBE:
			info.loss_trigger = 2;
			break;
		case ICSK_TIME_RETRANS:
			info.loss_trigger = 3;
			break;
		default:
			info.loss_trigger = 0;
		}
		info.seq = -1;

		if (info.loss_trigger > 0)
			mark_lost.perf_submit(ctx, &info, sizeof(info));
	}
}


static u32 get_tcp_reo_wnd(const struct sock *sk){
	struct tcp_sock *tp = tcp_sk(sk);
	struct inet_connection_sock* icsk = (struct inet_connection_sock *)sk;

	u32 min_rtt = tp->rtt_min.s[0].v;
	u8 reo_steps = tp->rack.reo_wnd_steps;
	u32 srtt = tp->srtt_us;
	u32 reo_wnd = min((min_rtt >> 2) * reo_steps, srtt >> 3);

	return reo_wnd;
}

void trace_rack_timer(struct pt_regs *ctx, struct sock *sk) {
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct timer_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;
		
		struct tcp_sock *tp = tcp_sk(sk);
		info.type = 1;
		u32 lrtt = tp->rack.rtt_us;
		u32 reo_wnd = get_tcp_reo_wnd(sk);
		info.timer = lrtt - reo_wnd;

		timer_calc.perf_submit(ctx, &info, sizeof(info));
	}
}

void trace_probe_timer(struct pt_regs *ctx, struct sock *sk) {
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct timer_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;
		
		struct tcp_sock *tp = tcp_sk(sk);
		info.type = 2;

		u32 timeout;
		u32 srtt = tp->srtt_us; 
		if (srtt) {
			timeout = srtt >> 2;
			u32 packets_out = tp->packets_out;
			if (packets_out == 1)
				timeout += jiffiestousecs(TCP_RTO_MIN);
			else
				timeout += jiffiestousecs(TCP_TIMEOUT_MIN);
		} else {
			timeout = jiffiestousecs(TCP_TIMEOUT_INIT);
		}
		info.timer = timeout;

		timer_calc.perf_submit(ctx, &info, sizeof(info));
	}
}