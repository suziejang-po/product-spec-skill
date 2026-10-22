"""흐름도 가상 예시 2개 (커리어 세미나 신청, 가상 프로젝트)
실행: {스펙 폴더}/diagrams/ 에서 python3 이 파일 → *.svg 생성 → render_svg.py로 PNG
좌표는 손으로 정한다. 자동 배치보다 읽기 쉬운 그림이 나온다
- 예시 1: 담당자 띠만 있는 흐름 (세미나 신청과 대기)
- 예시 2: 담당자 띠 + 단계 열 (세미나 운영)
"""
import os
import sys

sys.path.insert(0, os.environ.get("SKILL_SCRIPTS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")))
from svgkit import Chart  # noqa: E402

charts = {}

# ---------------- 예시 1. 세미나 신청과 대기 (담당자 띠) ----------------
c = Chart(1640, 560, '세미나 신청 플로우')
c.lane(80, 170, '참석자', '#F7FAFF')
c.lane(270, 260, '시스템', '#FAFBFC')
ty, my = 165, 400
c.box('t1', 260, ty, '세미나 상세\n신청하기', 'user', w=200)
c.box('t2', 510, ty, '신청 정보 확인', 'user', w=160)
c.box('t3', 730, ty, '신청 완료 또는\n대기 안내 화면', 'user', w=190)
c.diamond('m1', 510, my, '로그인?', w=130, h=76)
c.box('mlogin', 510, 500, 'OneID 로그인\n뒤 같은 화면으로', 'sys', w=180)
c.diamond('m2', 950, my, '정원 남음?', w=150, h=80)
c.box('mok', 1170, my, '신청 완료\n알림 발송', 'ok', w=180)
c.diamond('m3', 950, 200, '대기 자리\n남음?', w=150, h=84)
c.box('mwait', 1170, 200, '대기 등록\n대기 순번 안내', 'user', w=190)
c.box('mx', 1400, 200, '막힘 안내\n신청이 마감됐어요', 'bad', w=200)
c.box('m5', 1400, my, '내 신청 내역으로 이동', 'ok', w=200)
c.arrow([c.p('t1', 'r'), c.p('t2', 'l')])
c.arrow([c.p('t2', 'b'), c.p('m1', 't')])
c.arrow([c.p('m1', 'b'), c.p('mlogin', 't')], '아니오', 520, 455, la='start')
c.arrow([c.p('m1', 'r'), c.p('m2', 'l')], '예', 700, my - 8)
c.arrow([c.p('m2', 'r'), c.p('mok', 'l')], '예', 1075, my - 8)
c.arrow([c.p('m2', 't'), c.p('m3', 'b')], '아니오', 960, 300, la='start')
c.arrow([c.p('m3', 'r'), c.p('mwait', 'l')], '예', 1075, 192)
c.arrow([c.p('mwait', 'r'), c.p('mx', 'l')], dashed=True)
c.arrow([c.p('mok', 'r'), c.p('m5', 'l')])
c.arrow([c.p('t2', 'r'), c.p('t3', 'l')])
c.note(260, 235, '모집 기간에만 신청 가능', anchor='middle')
charts['apply_flow'] = c

# ---------------- 예시 2. 세미나 운영 (담당자 띠 + 단계 열) ----------------
c = Chart(1400, 820, '세미나 운영 플로우')
cols = [('준비', '어드민에서 생성'), ('모집', '신청과 대기'), ('신청 마감', '정원 확정'), ('진행', '세미나 당일'), ('종료', '')]
x0, cw = 140, 248
for i, (t, s) in enumerate(cols):
    c.column_header(x0 + i * cw + 6, 70, cw - 12, t, s or None)
    if i:
        c.vline(x0 + i * cw, 125, 790)
c.lane(130, 210, '운영자', '#FFFDF5', labelw=96)
c.lane(352, 230, '참석자', '#F7FAFF', labelw=96)
c.lane(594, 196, '호스트', '#FAFBFC', labelw=96)
cx = lambda i: x0 + i * cw + cw / 2
oy, uy, hy = 235, 467, 692
c.box('o1', cx(0), oy - 50, '세미나 만들기\n정원, 모집 기간', 'ops', w=200)
c.box('o2', cx(0), oy + 50, '미리보기 → 공개 전환', 'ops', w=200)
c.box('u1', cx(1), uy, '신청\n정원이 차면 대기', 'user', w=200)
c.note(cx(1), uy + 50, '시작 24시간 전까지 취소 가능', anchor='middle')
c.box('o3', cx(2), oy, '신청자 확인\n필요하면 반려', 'ops', w=200)
c.box('u2', cx(2), uy, '신청 상태 확인\n내 신청 내역', 'user', w=200)
c.box('h1', cx(3), hy, '출석 체크', 'sys', w=180)
c.box('u3', cx(3), uy, '세미나 참석', 'user', w=180)
c.box('o4', cx(4), oy, '출석 결과 확인\n다음 안내 대상 고름', 'ops', w=210)
c.box('u4', cx(4), uy, '프로필에\n참석한 세미나 표시', 'user', w=200)
c.arrow([c.p('o1', 'b'), c.p('o2', 't')])
c.arrow([c.p('o2', 'r'), (cx(1), oy + 50), c.p('u1', 't')])
c.arrow([c.p('u1', 'r'), c.p('u2', 'l')])
c.arrow([c.p('u2', 't'), c.p('o3', 'b')], '반려 건', cx(2) + 8, 360, la='start')
c.arrow([c.p('u2', 'r'), c.p('u3', 'l')])
c.arrow([c.p('u3', 'b'), c.p('h1', 't')])
c.arrow([c.p('h1', 'r'), (cx(4), hy), c.p('u4', 'b')])
c.arrow([c.p('u4', 't'), c.p('o4', 'b')])
charts['seminar_flow'] = c

if __name__ == "__main__":
    for name, ch in charts.items():
        open(f"{name}.svg", "w", encoding="utf-8").write(ch.svg())
        print(f"{name}.svg")
