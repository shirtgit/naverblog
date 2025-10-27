from data.list_data import ListData
import random

class TitleData:
    def __init__(self, address, company):
        self.title_data = ListData()
        self.title_list = []
        self.set_title_list()
        self.transfer_title(address, company)

    def set_title_list(self):
        title_list = self.title_data.title_list
        for idx in range(title_list.GetItemCount()):
            self.title_list.append(title_list.GetItemText(idx))

    def transfer_title(self, address, company):
        for idx in range(0, len(self.title_list)):
            self.title_list[idx] = self.title_list[idx].replace("%주소%", address)
            self.title_list[idx] = self.title_list[idx].replace("%업체%", company)

    def get_one_title_random(self):
        return random.choice(self.title_list)

