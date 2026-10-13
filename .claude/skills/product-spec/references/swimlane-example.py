"""흐름도 예시 (원티드 AI 빌더 허브 스펙에서 실제로 쓴 그림 2개)
실행: {스펙 폴더}/diagrams/ 에서 python3 이 파일 → *.svg 생성 → render_svg.py로 PNG
좌표는 손으로 정한다. 자동 배치보다 읽기 쉬운 그림이 나온다
- 예시 1: 담당자 띠만 있는 흐름 (팀 초대)
- 예시 2: 담당자 띠 + 단계 열 (프로그램 운영)
"""
import os
import sys

sys.path.insert(0, os.environ.get("SKILL_SCRIPTS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")))
from svgkit import Chart  # noqa: E402

charts = {}

# ---------------- 예시 1. 팀 초대 (담당자 띠) ----------------
c = Chart(1640, 560, '팀 초대 플로우')
c.lane(80, 170, '팀장', '#F7FAFF')
c.lane(270, 260, '팀원', '#F7FAFF')
ty, my = 165, 400
c.box('t1', 260, ty, '서비스 등록 화면\n소유 형태 팀, 팀명 입력', 'user', w=220)
c.box('t2', 510, ty, '임시 저장', 'user', w=140)
c.box('t3', 730, ty, '초대 링크 복사\n팀원에게 전달', 'user', w=190)
c.box('m1', 730, my, '초대 링크 열기', 'user', w=170)
c.diamond('m2', 950, my, '로그인?', w=130, h=76)
c.box('mlogin', 950, 500, 'OneID 로그인\n뒤 같은 화면으로', 'sys', w=180)
c.diamond('m3', 1170, my, '합류 가능?', w=150, h=80)
c.box('mx', 1170, 200, '막힘 안내\n링크 만료, 제출 마감,\n정원 초과, 이미 합류', 'bad', w=210)
c.box('m4', 1400, my, '이름 공개 선택\n팀에 합류하기', 'user', w=190, bold=True)
c.box('m5', 1400, 500, '내 서비스로 이동', 'ok', w=180)
c.arrow([c.p('t1', 'r'), c.p('t2', 'l')])
c.arrow([c.p('t2', 'r'), c.p('t3', 'l')])
c.arrow([c.p('t3', 'b'), c.p('m1', 't')])
c.arrow([c.p('m1', 'r'), c.p('m2', 'l')])
c.arrow([c.p('m2', 'b'), c.p('mlogin', 't')], '아니오', 960, 455, la='start')
c.arrow([c.p('mlogin', 'r'), (1080, 500), (1080, my), (1095, my)])
c.arrow([c.p('m2', 'r'), c.p('m3', 'l')], '예', 1055, my - 8)
c.arrow([c.p('m3', 't'), c.p('mx', 'b')], '아니오', 1180, 300, la='start')
c.arrow([c.p('m3', 'r'), c.p('m4', 'l')], '예', 1285, my - 8)
c.arrow([c.p('m4', 'b'), c.p('m5', 't')])
c.note(260, 235, '팀장 포함 최대 5명 (프로그램은 설정값)', anchor='middle')
charts['team_invite'] = c

# ---------------- 예시 2. 프로그램 운영 (담당자 띠 + 단계 열) ----------------
c = Chart(1900, 820, '프로그램 운영 플로우')
cols = [('준비', 'HQ에서 생성'), ('접수', '참가 신청'), ('제출', '서비스 등록'), ('공개', '열람만'), ('공개+추천', '추천 가능 기간'), ('결과 발표', '확정 순위'), ('종료', '')]
x0, cw = 140, 248
for i, (t, s) in enumerate(cols):
    c.column_header(x0 + i * cw + 6, 70, cw - 12, t, s or None)
    if i:
        c.vline(x0 + i * cw, 125, 790)
c.lane(130, 210, '운영자', '#FFFDF5', labelw=96)
c.lane(352, 230, '유저', '#F7FAFF', labelw=96)
c.lane(594, 196, '시스템', '#FAFBFC', labelw=96)
cx = lambda i: x0 + i * cw + cw / 2
oy, uy, sy = 235, 467, 692
c.box('o1', cx(0), oy - 50, '프로그램 만들기\n임시 저장', 'ops', w=200)
c.box('o2', cx(0), oy + 50, '미리보기 → 공개 전환\n배너 편성', 'ops', w=200)
c.box('u1', cx(1), uy, '참가 신청\n(접수 구간 있는 경우)', 'user', w=210)
c.box('u2', cx(2) - 30, uy, '서비스 등록\n검수 요청', 'user', w=170)
c.note(cx(2) - 30, uy - 52, '접수 구간이 있으면 신청한 사람만', anchor='middle')
c.box('o3', cx(2), oy, '검수 대기 처리\n제출 마감 전에 끝내기', 'ops', w=210)
c.box('s1', cx(2) - 30, sy, 'AI 자동 점검', 'sys', w=160)
c.box('s2', cx(3), sy, '프로그램 안에\n서비스 노출 시작', 'sys', w=190)
c.box('u3', cx(3), uy, '서비스 열람', 'user', w=180)
c.box('u4', cx(4), uy, '추천\n1명이 서비스 1개에 1번', 'user', w=210)
c.note(cx(4), uy + 50, '취소는 프로그램 설정에 따라', anchor='middle')
c.box('s3', cx(4), sy, '프로그램 리더보드\n집계 중 순위', 'sys', w=200)
c.box('o4', cx(5), oy, '최종 순위, 수상 입력\n확정', 'ops', w=210)
c.box('u5', cx(5), uy, '확정 순위와\n수상 확인', 'user', w=180)
c.box('o5', cx(6), oy, '수상자 뱃지 부여\n(기존 HQ 뱃지 기능)', 'ops', w=200)
c.box('s4', cx(6), sy, '마지막 구간 종료 뒤\n자동 종료, 목록에 남음', 'sys', w=210)
c.arrow([c.p('o1', 'b'), c.p('o2', 't')])
c.arrow([c.p('o2', 'r'), (cx(1), oy + 50), c.p('u1', 't')])
c.arrow([c.p('u1', 'r'), c.p('u2', 'l')])
c.arrow([c.p('u2', 'b'), c.p('s1', 't')])
c.arrow([c.p('s1', 'r'), (cx(2) + 118, sy), (cx(2) + 118, oy), (cx(2) + 105, oy)], '주의 건', cx(2) + 124, sy - 60, la='start')
c.arrow([c.p('s1', 'b'), (cx(2) - 30, sy + 62), (cx(3), sy + 62), c.p('s2', 'b')], '통과, 게시 건', (cx(2) + cx(3)) / 2, sy + 56)
c.arrow([c.p('s2', 't'), c.p('u3', 'b')])
c.arrow([c.p('u3', 'r'), c.p('u4', 'l')])
c.arrow([c.p('u4', 'b'), c.p('s3', 't')])
c.arrow([c.p('s3', 'r'), (cx(5) - 125, sy), (cx(5) - 125, oy), c.p('o4', 'l')])
c.arrow([c.p('o4', 'b'), c.p('u5', 't')])
c.arrow([c.p('o4', 'r'), c.p('o5', 'l')])
charts['program_flow'] = c

if __name__ == "__main__":
    for name, ch in charts.items():
        open(f"{name}.svg", "w", encoding="utf-8").write(ch.svg())
        print(f"{name}.svg")
