import random

class ContentData:
    _instance = None
    _initialized = False  # 여기서 플래그 설정

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContentData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if ContentData._initialized:
            return  # 이미 초기화된 경우, 바로 리턴

        self.keywords = None
        self.image_path = None
        self.keywords_concat = None
        self.hashtags = None

        ContentData._initialized = True

    def set_keywords(self, keyword):
        for i, row in enumerate(keyword):
            if all(cell == '' for cell in row):
                self.keywords = keyword[:i]
                return
        self.keywords = keyword  # 모두 비어있지 않다면 원본 그대로

    def combinate_keywords(self):
        # address, company = zip(*self.keywords)
        # self.keywords = [[x, y] for x in address for y in company]

        result = []

        for i in range(0, len(self.keywords)):
            if self.keywords[i][0] == "":
                break
            for j in range(0, len(self.keywords)):
                if self.keywords[j][1] == "":
                    continue
                result.append([self.keywords[i][0], self.keywords[j][1]])

        self.keywords = result

    def get_address(self, row):
        return self.keywords[row][0]

    def get_company(self, row):
        return self.keywords[row][1]

    def get_keywords_length(self):
        return len(self.keywords)

    def set_image_path(self, path):
        for i, row in enumerate(path):
            if all(cell == '' for cell in row):
                self.image_path = path[:i]
                return
        self.image_path = path  # 모두 비어있지 않다면 원본 그대로

    def get_random_image_path(self, num):
        # print(self.image_path)
        return random.sample(self.image_path, num)

    def get_image_path_length(self):
        return len(self.image_path)

    def set_keywords_concat(self, keywords_concat):
        self.keywords_concat = keywords_concat

    def set_hashtags(self, hashtags):
        for i, row in enumerate(hashtags):
            if all(cell == '' for cell in row):
                self.hashtags = hashtags[:i]
                return
        self.hashtags = hashtags  # 모두 비어있지 않다면 원본 그대로

    def get_hashtags(self):
        return self.hashtags