hashtags = ["%주소% %업체% 1", "%주소% %업체% 2", "%주소% %업체% 3"]
address = "성수동"
company = "설비업체"

for idx in range(len(hashtags)):
    hashtags[idx] = hashtags[idx].replace("%주소%", address)
    hashtags[idx] = hashtags[idx].replace("%업체%", company)

print(hashtags)

hashtags = ["%주소% %업체% 1", "%주소% %업체% 2", "%주소% %업체% 3"]
address = "성수동"
company = "설비업체"

for hashtag in hashtags:
    hashtag = hashtag.replace("%주소%", address)
    hashtag = hashtag.replace("%업체%", company)
    print(hashtag)