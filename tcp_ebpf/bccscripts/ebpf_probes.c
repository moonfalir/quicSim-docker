#define KBUILD_MODNAME "tcpcctrace"
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <net/tcp.h>

struct congestion_info {
	u64 timestamp;
	u32 saddr;
	u32 daddr;
	u16 sport;
    u16 dport;
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
	u32 daddr;
	u16 sport;
    u16 dport;
    u64 timestamp;
    u8 new_state;
};
BPF_PERF_OUTPUT(tcp_events);
BPF_PERF_OUTPUT(ca_state);


void trace_rcv_established(struct pt_regs *ctx, struct sock *sk)
{
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
    	struct congestion_info info = {};
		info.saddr = sk->__sk_common.skc_rcv_saddr;
		info.daddr = sk->__sk_common.skc_daddr;
		info.sport = sk->__sk_common.skc_num;
		u16 dport = sk->__sk_common.skc_dport;
		info.dport = ntohs(dport);
    	const struct tcp_sock *tp = tcp_sk(sk);
    	info.snd_cwnd = tp->snd_cwnd; //Sending congestion window
		info.min_rtt = tp->rtt_min.s[0].v;
		info.smoothed_rtt = tp->srtt_us >> 3; //smoothed round trip time << 3 in usecs
		info.latest_rtt = tp->rack.rtt_us; // Information of the most recently (s)acked skb
		info.bytes_sent = tp->bytes_sent;
		info.bytes_acked = tp->bytes_acked;
		info.ssthresh = tp->snd_ssthresh; //Slow start size threshold

		info.timestamp = bpf_ktime_get_ns();
    	tcp_events.perf_submit(ctx, &info, sizeof(info));
	}
}

void trace_cubictcp_state(struct pt_regs *ctx, struct sock *sk, u8 new_state) {
    u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
        struct ca_init_info info = {};
        info.saddr = sk->__sk_common.skc_rcv_saddr;
		info.daddr = sk->__sk_common.skc_daddr;
		info.sport = sk->__sk_common.skc_num;
		u16 dport = sk->__sk_common.skc_dport;
		info.dport = ntohs(dport);
        info.new_state = new_state;

        info.timestamp = bpf_ktime_get_ns();
    	ca_state.perf_submit(ctx, &info, sizeof(info));
	}
}