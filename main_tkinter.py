import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys

class BlogPostingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("네이버 포스팅 자동화 프로그램")
        self.root.geometry("1200x800")
        
        # 메인 프레임
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 왼쪽 패널
        self.create_left_panel(main_frame)
        
        # 중앙 패널
        self.create_middle_panel(main_frame)
        
        # 오른쪽 패널 (로그)
        self.create_right_panel(main_frame)
        
    def create_left_panel(self, parent):
        # 왼쪽 프레임
        left_frame = ttk.LabelFrame(parent, text="설정", width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # 현재 상태
        status_frame = ttk.Frame(left_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(status_frame, text="현재 상태:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="블로그", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 플랫폼 선택
        platform_frame = ttk.LabelFrame(left_frame, text="플랫폼 선택")
        platform_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.platform_var = tk.StringVar(value="블로그")
        ttk.Radiobutton(platform_frame, text="블로그", variable=self.platform_var, 
                       value="블로그", command=self.on_platform_change).pack(anchor=tk.W)
        ttk.Radiobutton(platform_frame, text="카페", variable=self.platform_var, 
                       value="카페", command=self.on_platform_change).pack(anchor=tk.W)
        ttk.Radiobutton(platform_frame, text="둘 다", variable=self.platform_var, 
                       value="둘 다", command=self.on_platform_change).pack(anchor=tk.W)
        
        # 대기시간 설정
        waiting_frame = ttk.LabelFrame(left_frame, text="대기시간 설정")
        waiting_frame.pack(fill=tk.X, padx=5, pady=5)
        
        time_frame = ttk.Frame(waiting_frame)
        time_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(time_frame, text="최소(분):").grid(row=0, column=0, sticky=tk.W)
        self.min_wait = ttk.Entry(time_frame, width=10)
        self.min_wait.grid(row=0, column=1, padx=(5, 0))
        self.min_wait.insert(0, "1")
        
        ttk.Label(time_frame, text="최대(분):").grid(row=1, column=0, sticky=tk.W)
        self.max_wait = ttk.Entry(time_frame, width=10)
        self.max_wait.grid(row=1, column=1, padx=(5, 0))
        self.max_wait.insert(0, "3")
        
        # 유동 IP 사용
        self.ip_toggle = tk.BooleanVar(value=True)
        ttk.Checkbutton(waiting_frame, text="유동 IP 사용여부", 
                       variable=self.ip_toggle).pack(anchor=tk.W, padx=5, pady=2)
        
        # API KEY
        api_frame = ttk.LabelFrame(left_frame, text="API 설정")
        api_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(api_frame, text="API KEY:").pack(anchor=tk.W, padx=5)
        self.api_key = ttk.Entry(api_frame)
        self.api_key.pack(fill=tk.X, padx=5, pady=2)
        
        # 핸드폰 번호
        phone_frame = ttk.LabelFrame(left_frame, text="인증")
        phone_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(phone_frame, text="핸드폰 번호:").pack(anchor=tk.W, padx=5)
        self.phone_number = ttk.Entry(phone_frame)
        self.phone_number.pack(fill=tk.X, padx=5, pady=2)
        
        # 계정 업로드
        account_frame = ttk.LabelFrame(left_frame, text="계정 관리")
        account_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(account_frame, text="계정 업로드", 
                  command=self.upload_accounts).pack(fill=tk.X, padx=5, pady=2)
        
        # 계정 리스트
        self.account_list = ttk.Treeview(account_frame, columns=("password", "location"), show="tree headings", height=6)
        self.account_list.heading("#0", text="계정명")
        self.account_list.heading("password", text="비밀번호")
        self.account_list.heading("location", text="장소")
        self.account_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # 키워드 업로드
        keyword_frame = ttk.LabelFrame(left_frame, text="키워드 관리")
        keyword_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(keyword_frame, text="키워드 업로드", 
                  command=self.upload_keywords).pack(fill=tk.X, padx=5, pady=2)
        
        # 키워드 리스트
        self.keyword_list = ttk.Treeview(keyword_frame, columns=("company", "filepath", "hashtag"), show="tree headings", height=6)
        self.keyword_list.heading("#0", text="주소")
        self.keyword_list.heading("company", text="업체")
        self.keyword_list.heading("filepath", text="파일 경로")
        self.keyword_list.heading("hashtag", text="해시태그")
        self.keyword_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
    def create_middle_panel(self, parent):
        # 중앙 프레임
        middle_frame = ttk.LabelFrame(parent, text="콘텐츠 작성", width=400)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        middle_frame.pack_propagate(False)
        
        # 제목 업로드
        title_frame = ttk.Frame(middle_frame)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(title_frame, text="제목 업로드", 
                  command=self.upload_titles).pack(side=tk.LEFT)
        
        # 제목 리스트
        self.title_list = ttk.Treeview(middle_frame, columns=(), show="tree headings", height=6)
        self.title_list.heading("#0", text="제목")
        self.title_list.pack(fill=tk.X, padx=5, pady=5)
        
        # 안내문
        info_text = """
[폼 형식 지정 안내글]

[본문]을 기준으로 서론, 본문, 결론으로 나뉘어집니다.

본문은 AI로 작성한 1500자 내외의 글이며,
고객님께서 keyword.csv를 통해 업로드한 이미지 중 랜덤으로 5개가 같이 들어갑니다.

keyword.csv에서 받아온 정보 중에서
%주소% 문자열은 주소 열의 데이터를, %업체% 문자열은 업체 열의 데이터로 치환됩니다.

%썸네일% 문자열은 썸네일 사진으로, %영상% 문자열은 썸네일 사진을 바탕으로 제작된 영상으로 치환됩니다.
        """
        
        info_frame = ttk.LabelFrame(middle_frame, text="사용 안내")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, wraplength=350)
        info_label.pack(padx=5, pady=5)
        
        # 콘텐츠 입력
        content_frame = ttk.LabelFrame(middle_frame, text="콘텐츠 입력")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.content_text = scrolledtext.ScrolledText(content_frame, height=15, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 기본 템플릿 삽입
        template = """안녕하세요. 헤더입니다. 여기서 등록하는 미디어는 테스트를 위한 임의의 사진 및 영상입니다.

[사진]

이곳부터는 AI가 작성할 글이 들어갈 본문입니다.

[사진]

이 밑에는 영상이 들어갑니다.

[영상]

맺음말입니다."""
        
        self.content_text.insert(tk.END, template)
        
        # 작업 수행 버튼
        ttk.Button(middle_frame, text="작업 수행", 
                  command=self.execute_task).pack(fill=tk.X, padx=5, pady=5)
        
    def create_right_panel(self, parent):
        # 오른쪽 프레임 (로그)
        right_frame = ttk.LabelFrame(parent, text="로그 화면", width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        self.log_text = scrolledtext.ScrolledText(right_frame, height=30, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 초기 로그 메시지
        self.log("프로그램이 시작되었습니다.")
        self.log("wxPython 대신 tkinter로 구현된 버전입니다.")
        
    def on_platform_change(self):
        platform = self.platform_var.get()
        self.status_label.config(text=platform)
        self.log(f"플랫폼이 {platform}로 변경되었습니다.")
        
    def upload_accounts(self):
        file_path = filedialog.askopenfilename(
            title="계정 파일 선택",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.log(f"계정 파일 업로드: {file_path}")
            # 여기에 실제 파일 처리 로직 추가
            
    def upload_keywords(self):
        file_path = filedialog.askopenfilename(
            title="키워드 파일 선택",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.log(f"키워드 파일 업로드: {file_path}")
            # 여기에 실제 파일 처리 로직 추가
            
    def upload_titles(self):
        file_path = filedialog.askopenfilename(
            title="제목 파일 선택",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.log(f"제목 파일 업로드: {file_path}")
            # 여기에 실제 파일 처리 로직 추가
            
    def execute_task(self):
        self.log("작업 수행을 시작합니다...")
        self.log("API KEY: " + (self.api_key.get() or "설정되지 않음"))
        self.log("핸드폰 번호: " + (self.phone_number.get() or "설정되지 않음"))
        self.log("플랫폼: " + self.platform_var.get())
        self.log("유동 IP 사용: " + ("예" if self.ip_toggle.get() else "아니오"))
        self.log("콘텐츠 길이: " + str(len(self.content_text.get("1.0", tk.END))) + " 문자")
        self.log("작업이 완료되었습니다.")
        
    def log(self, message):
        self.log_text.insert(tk.END, f"[{self.get_timestamp()}] {message}\n")
        self.log_text.see(tk.END)
        
    def get_timestamp(self):
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

def main():
    root = tk.Tk()
    app = BlogPostingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
