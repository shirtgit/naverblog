import random

class Colors:
    def __init__(self):
        self.color_map = {
            "text": [
                "white", "black", "red", "blue", "yellow", "green", "orange",

                "gold", "pink", "plum", "coral", "salmon", "orchid",

                "hotpink", "greenyellow", "tomato", "wheat", "seagreen", "lightcoral", "navy", "crimson",

                "khaki", "violet", "skyblue", "forestgreen", "cadetblue", "rosybrown", "steelblue", "slateblue",

                "palegreen", "lemonchiffon", "darkseagreen", "sienna", "peru",

                "moccasin", "antiquewhite", "aliceblue", "burlywood", "azure",

                "blanchedalmond", "ivory", "mintcream",

                "whitesmoke", "darkgoldenrod", "firebrick", "darkred", "darkblue", "darkgreen", "darkslateblue",

                "mediumvioletred", "mediumslateblue", "mediumspringgreen", "olivedrab", "palevioletred",

                "peachpuff", "rebeccapurple", "slategray", "tan", "teal", "darkslategray"
            ],
            "bg": [
                "black", "white", "navy", "ivory", "midnightblue", "whitesmoke", "darkblue",

                "maroon", "darkslategray", "saddlebrown", "azure", "brown", "mintcream",

                "wheat", "indianred", "seashell", "chocolate", "floralwhite", "darkolivegreen", "firebrick", "linen",

                "lightcoral", "lavenderblush", "orangered", "papayawhip", "lemonchiffon", "indigo", "navy", "bisque",

                "dimgray", "gray", "wheat", "tan", "antiquewhite",

                "black", "darkslategray", "gray", "snow", "maroon",

                "blue", "brown", "navy",

                "purple", "azure", "teal", "cornsilk", "red", "papayawhip", "lemonchiffon",

                "blanchedalmond", "burlywood", "maroon", "black", "antiquewhite",

                "forestgreen", "chocolate", "linen", "slateblue", "oldlace", "mintcream"
            ]
            # "text": [
            #     "white",
            #     "black",
            #     "white",
            #     "black",
            #     "lime",
            #     "white",
            #     "white",
            #     "white",
            #     "dimgray",
            #     "yellow"
            # ],
            # "bg": [
            #     "black",
            #     "white",
            #     "midnightblue",
            #     "yellow",
            #     "dimgray",
            #     "darkgreen",
            #     "orangered",
            #     "indigo",
            #     "whitesmoke",
            #     "navy"
            # ]
        }

    def get_random_colors(self):
        length = len(self.color_map["bg"])
        index = random.randint(0, length - 1)
        return self.color_map["bg"][index], self.color_map["text"][index]

    def get_color(self, index):
        return self.color_map["bg"][index], self.color_map["text"][index]

    def get_one_random_color(self):
        length = len(self.color_map["bg"])
        index = random.randint(0, length - 1)
        return self.color_map["bg"][index]

    def get_color_length(self):
        return len(self.color_map["bg"])
