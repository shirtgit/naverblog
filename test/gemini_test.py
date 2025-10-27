from ai import gemini
from data import const

gemini.init_gemini()
response = gemini.create_content([const.CONTENT_EX1, const.CONTENT_EX2])
print(response)

