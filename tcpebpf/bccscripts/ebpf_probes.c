#define KBUILD_MODNAME "tcpcctrace"
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <net/tcp.h>

#define MIN(a,b) ((a) < (b) ? (a) : (b))

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

struct ca_init_info {
    u32 saddr;
    u64 timestamp;
    u8 new_state;
};

struct ca_ssthresh_info {
	u32 saddr;
    u64 timestamp;
	u32 ssthresh;
	u32 last_max_cwnd;
};

struct cwnd_event_info {
	u32 saddr;
    u64 timestamp;
	int event_type;
};

struct cwnd_info {
	u32 saddr;
    u64 timestamp;
	u32 snd_cwnd;
	u32 pkts_in_flight;
	u32 min_rtt;
	u32 smoothed_rtt;
	u32 latest_rtt;
	//u32 ack_cnt;
	//u32 cnt;
	//u32 bic_K;
	//u32 bic_origin_point;
};

struct loss_info {
	u32 saddr;
    u64 timestamp;
	u32 loss_seq;
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

struct flow_ctrl_info {
	u32 saddr;
    u64 timestamp;
	u64 bytes_in_flight;
};

// eBPF tables to output data
BPF_PERF_OUTPUT(tcp_events);
BPF_PERF_OUTPUT(ca_state);
BPF_PERF_OUTPUT(ssthresh_event);
BPF_PERF_OUTPUT(cwnd_event);
BPF_PERF_OUTPUT(cwnd_change);
BPF_PERF_OUTPUT(loss_event);
BPF_PERF_OUTPUT(init_event);
BPF_PERF_OUTPUT(fc_event);

// Trace cubic TCP state changes
void trace_cubictcp_state(struct pt_regs *ctx, struct sock *sk, u8 new_state) {
    u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
        struct ca_init_info info = {};
		info.timestamp = bpf_ktime_get_ns();
        info.saddr = sk->__sk_common.skc_rcv_saddr;
        info.new_state = new_state;

    	ca_state.perf_submit(ctx, &info, sizeof(info));
	}
}

// Trace changes to ssthresh
void trace_recalc_ssthresh(struct pt_regs *ctx, struct sock *sk) {
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct ca_ssthresh_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;
		const struct bictcp *ca = inet_csk_ca(sk);

		u32 retval = regs_return_value(ctx);
		info.ssthresh = retval;
		info.last_max_cwnd = ca->last_max_cwnd;
		ssthresh_event.perf_submit(ctx, &info, sizeof(info));
	}
}

// trace CWND events
void trace_cwnd_event(struct pt_regs *ctx, struct sock *sk, enum tcp_ca_event event) {
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct cwnd_event_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;

		info.event_type = event;
		cwnd_event.perf_submit(ctx, &info, sizeof(info));
	}
}

/**
 * Implementation of https://elixir.bootlin.com/linux/v5.0/source/net/ipv4/tcp_cong.c#L407 
 * Function does not return new CWND value so can't use return probe
 **/
static u32 calc_new_cwnd(struct pt_regs *ctx, struct tcp_sock *tp, u32 w, u32 acked) {
	u32 snd_cwnd_cnt = tp->snd_cwnd_cnt;
	u32 snd_cwnd = tp->snd_cwnd;
	u32 snd_cwnd_clamp = tp->snd_cwnd_clamp;

	/* If credits accumulated at a higher w, apply them gently now. */
	if (snd_cwnd_cnt >= w) {
		snd_cwnd_cnt = 0;
		snd_cwnd++;
	}
	
	snd_cwnd_cnt += acked;
	if (snd_cwnd_cnt >= w) {
		u32 delta = snd_cwnd_cnt / w;

		snd_cwnd_cnt -= delta * w;
		snd_cwnd += delta;
	}
	snd_cwnd = MIN(snd_cwnd, snd_cwnd_clamp);
	return snd_cwnd;
}

// Trace CWND changes during congestion avoidance
void trace_cong_avoid(struct pt_regs *ctx, struct tcp_sock *tp, u32 w, u32 acked) {
	const struct sock *sk = &(tp->inet_conn.icsk_inet.sk);
	u16 family = sk->__sk_common.skc_family;
	
	if (family == AF_INET) {
		struct cwnd_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;
		//const struct bictcp *ca = inet_csk_ca(sk);

		info.min_rtt = tp->rtt_min.s[0].v;
		info.smoothed_rtt = tp->srtt_us >> 3;
		info.latest_rtt = tp->rack.rtt_us;
		//if (tp->snd_cwnd < tp->snd_ssthresh){
		//	u32 snd_cwnd = tp->snd_cwnd;
		//	u32 snd_cwnd_clamp = tp->snd_cwnd_clamp;
		//	u32 ssthresh = tp->snd_ssthresh;
		//	u32 cwnd = MIN(snd_cwnd + acked, ssthresh);
		//	info.snd_cwnd = MIN(cwnd, snd_cwnd_clamp);
		//}
		//else
		//	info.snd_cwnd = calc_new_cwnd(ctx, tp, w, acked);
		info.snd_cwnd = tp->snd_cwnd;

		//if (acked <= tp->packets_out)
		//	info.pkts_in_flight = tp->packets_out - acked;
		//else
		//	info.pkts_in_flight = 0;
		info.pkts_in_flight = tp->packets_out;
		//info.ack_cnt = ca->ack_cnt;
		//info.cnt = ca->cnt;
		//info.bic_K = ca->bic_K;
		//info.bic_origin_point = ca->bic_origin_point;
		cwnd_change.perf_submit(ctx, &info, sizeof(info));
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
		//u32 acked = regs_return_value(ctx);
		if (acked <= tp->packets_out)
			info.pkts_in_flight = tp->packets_out - acked;
		else
			info.pkts_in_flight = 0;
		cwnd_change.perf_submit(ctx, &info, sizeof(info));
	}
}

// Trace loss events
void trace_enter_loss(struct pt_regs *ctx, struct sock *sk) {
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct loss_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		const struct tcp_sock *tp = tcp_sk(sk);
		
		info.saddr = sk->__sk_common.skc_rcv_saddr;
		info.loss_seq = tp->snd_una;

		loss_event.perf_submit(ctx, &info, sizeof(info));
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

void trace_bytes_in_flight(struct pt_regs *ctx, struct sock *sk) {
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct flow_ctrl_info info = {};
		info.timestamp = bpf_ktime_get_ns();

		const struct tcp_sock *tp = tcp_sk(sk);

		info.saddr = sk->__sk_common.skc_rcv_saddr;
		if (tp->bytes_sent > tp->bytes_acked)
			info.bytes_in_flight = tp->bytes_sent - tp->bytes_acked;
		else
			info.bytes_in_flight = 0;

		fc_event.perf_submit(ctx, &info, sizeof(info));
	}
}