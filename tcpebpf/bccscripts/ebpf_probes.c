#define KBUILD_MODNAME "tcpcctrace"
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <net/tcp.h>

#define MIN(a,b) ((a) < (b) ? (a) : (b))

struct congestion_info {
	u64 timestamp;
	u32 saddr;
    u32 snd_cwnd;
	u32 min_rtt;
	u32 smoothed_rtt;
	u32 latest_rtt;
	u64 bytes_sent;
	u64 bytes_acked;
	u32 ssthresh;
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
};

struct loss_info {
	u32 saddr;
    u64 timestamp;
	u32 loss_seq;
};

BPF_PERF_OUTPUT(tcp_events);
BPF_PERF_OUTPUT(ca_state);
BPF_PERF_OUTPUT(ssthresh_event);
BPF_PERF_OUTPUT(cwnd_event);
BPF_PERF_OUTPUT(cwnd_change);
BPF_PERF_OUTPUT(loss_event);


void trace_rcv_established(struct pt_regs *ctx, struct sock *sk)
{
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
    	struct congestion_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;
    	const struct tcp_sock *tp = tcp_sk(sk);
    	info.snd_cwnd = tp->snd_cwnd; //Sending congestion window
		info.min_rtt = tp->rtt_min.s[0].v;
		info.smoothed_rtt = tp->srtt_us >> 3; //smoothed round trip time << 3 in usecs
		info.latest_rtt = tp->rack.rtt_us; // Information of the most recently (s)acked skb
		info.bytes_sent = tp->bytes_sent;
		info.bytes_acked = tp->bytes_acked;
		info.ssthresh = tp->snd_ssthresh; //Slow start size threshold

    	tcp_events.perf_submit(ctx, &info, sizeof(info));
	}
}

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

void trace_recalc_ssthresh(struct pt_regs *ctx, struct sock *sk) {
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct ca_ssthresh_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;

		u32 retval = regs_return_value(ctx);
		info.ssthresh = retval;
		ssthresh_event.perf_submit(ctx, &info, sizeof(info));
	}
}

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

void trace_cong_avoid(struct pt_regs *ctx, struct tcp_sock *tp, u32 w, u32 acked) {
	const struct sock *sk = &(tp->inet_conn.icsk_inet.sk);
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct cwnd_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;

		info.snd_cwnd = calc_new_cwnd(ctx, tp, w, acked);
		if (tp->snd_cwnd != info.snd_cwnd)
			cwnd_change.perf_submit(ctx, &info, sizeof(info));
	}
}

void trace_slow_start(struct pt_regs *ctx, struct tcp_sock *tp) {
	const struct sock *sk = &(tp->inet_conn.icsk_inet.sk);
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
		struct cwnd_info info = {};
		info.timestamp = bpf_ktime_get_ns();
		info.saddr = sk->__sk_common.skc_rcv_saddr;

		info.snd_cwnd = tp->snd_cwnd;
		cwnd_change.perf_submit(ctx, &info, sizeof(info));
	}
}

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