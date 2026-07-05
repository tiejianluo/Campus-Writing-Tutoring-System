"""K12 elementary English writing content: rubrics, templates, and topics.

Grade bands follow the domestic primary-school English curriculum: short
guided writing in grades 3-4, paragraph writing in grades 5-6.
"""

ENGLISH_GRADE_RUBRICS = {
    "三年级": {
        "rubric": [
            ("切题 Content", "是否围绕题目，写出图片或主题中的人和事"),
            ("词汇 Vocabulary", "能使用学过的单词，拼写基本正确"),
            ("句子 Sentences", "能写出完整的简单句（主语+动词）"),
            ("书写 Handwriting", "大小写和标点基本正确"),
        ],
        "target_words": (30, 50),
    },
    "四年级": {
        "rubric": [
            ("切题 Content", "内容切题，信息完整"),
            ("词汇 Vocabulary", "用词恰当，拼写正确"),
            ("句子 Sentences", "句子完整通顺，能用 and/but 连接"),
            ("结构 Structure", "有开头和结尾的意识"),
            ("书写 Mechanics", "大小写、标点、格式规范"),
        ],
        "target_words": (40, 60),
    },
    "五年级": {
        "rubric": [
            ("切题 Content", "内容切题、有细节"),
            ("词汇 Vocabulary", "词汇较丰富，会用形容词修饰"),
            ("语法 Grammar", "时态和人称基本正确"),
            ("结构 Structure", "有 beginning-middle-end，会用 first/then/finally"),
            ("书写 Mechanics", "拼写、标点、格式规范"),
        ],
        "target_words": (60, 80),
    },
    "六年级": {
        "rubric": [
            ("切题 Content", "内容完整，有自己的想法和感受"),
            ("词汇 Vocabulary", "词汇丰富多样，用词准确"),
            ("语法 Grammar", "时态一致，句式有变化（含 because/when 等从句）"),
            ("结构 Structure", "段落清晰，衔接自然"),
            ("书写 Mechanics", "拼写、标点、格式规范"),
        ],
        "target_words": (80, 120),
    },
}

ENGLISH_TEMPLATES = {
    "Picture Description 看图写话": {
        "结构": [
            "Beginning: say what/who is in the picture",
            "Middle: describe what they are doing",
            "Ending: say how you feel about it",
        ],
        "万能开头": "In the picture, I can see ...",
        "万能结尾": "What a nice picture! I like it very much.",
        "常用句型": ["There is/are ...", "He/She is ...ing", "They look very happy."],
        "grades": ["三年级", "四年级", "五年级", "六年级"],
    },
    "About Me / My Family 自我介绍": {
        "结构": [
            "Beginning: introduce yourself or your family",
            "Middle: give two or three details (age, hobby, job ...)",
            "Ending: say your feeling",
        ],
        "万能开头": "Hello! My name is ... I am ... years old.",
        "万能结尾": "This is me! / I love my family.",
        "常用句型": ["I have ...", "My father/mother is ...", "We like to ... together."],
        "grades": ["三年级", "四年级"],
    },
    "My Day 我的一天": {
        "结构": [
            "Beginning: when the day starts",
            "Middle: what you do in order (first / then / after that)",
            "Ending: how you feel about the day",
        ],
        "万能开头": "I get up at ... o'clock in the morning.",
        "万能结尾": "What a busy and happy day!",
        "常用句型": ["First, I ...", "Then I ...", "After school, I ...", "Finally, I go to bed at ..."],
        "grades": ["四年级", "五年级"],
    },
    "Diary 英语日记": {
        "结构": [
            "Beginning: date and weather",
            "Middle: one thing that happened today",
            "Ending: your feeling",
        ],
        "万能开头": "Monday, June 1st, Sunny. Today I ...",
        "万能结尾": "I had a good time today.",
        "常用句型": ["Today I ... with ...", "It was very ...", "I felt so happy/excited."],
        "grades": ["四年级", "五年级", "六年级"],
    },
    "My Hobby / My Best Friend 爱好与朋友": {
        "结构": [
            "Beginning: name the hobby or friend",
            "Middle: give details and one small example",
            "Ending: why you like it/him/her",
        ],
        "万能开头": "My hobby is ... / My best friend is ...",
        "万能结尾": "That is why I like ... so much.",
        "常用句型": ["I often ... after school.", "He/She is good at ...", "We always help each other."],
        "grades": ["五年级", "六年级"],
    },
    "Letter / Email 书信邮件": {
        "结构": [
            "Beginning: Dear ..., greeting",
            "Middle: the main message (2-4 sentences)",
            "Ending: wish + signature",
        ],
        "万能开头": "Dear Lily, How are you? I want to tell you about ...",
        "万能结尾": "Best wishes! / Yours, Ming",
        "常用句型": ["I am glad to ...", "Would you like to ...?", "Please write to me soon."],
        "grades": ["五年级", "六年级"],
    },
    "Story / My Dream 小故事与梦想": {
        "结构": [
            "Beginning: set the scene (who, when, where)",
            "Middle: what happened, step by step",
            "Ending: the result or what you learned",
        ],
        "万能开头": "One day, ... / I have a dream. I want to be ...",
        "万能结尾": "From then on, ... / I will work hard for my dream.",
        "常用句型": ["Suddenly, ...", "At last, ...", "I believe that ...", "If I ..., I will ..."],
        "grades": ["六年级"],
    },
}

ENGLISH_TOPICS = {
    "Picture Description 看图写话": ["A Happy Day in the Park", "My Classroom", "Playing Football"],
    "About Me / My Family 自我介绍": ["All About Me", "My Family", "My Pet"],
    "My Day 我的一天": ["My School Day", "My Weekend", "A Busy Sunday"],
    "Diary 英语日记": ["My Happy Day", "A Rainy Day", "Sports Day"],
    "My Hobby / My Best Friend 爱好与朋友": ["My Hobby", "My Best Friend", "Reading Is Fun"],
    "Letter / Email 书信邮件": ["A Letter to My Friend", "An Email to My Teacher", "Invite a Friend"],
    "Story / My Dream 小故事与梦想": ["My Dream", "A Small Kind Act", "The Lost Cat"],
}

ENGLISH_LINKING_WORDS = [
    "first", "then", "next", "after", "finally", "at last",
    "and", "but", "because", "so", "when", "suddenly",
]

ENGLISH_EXPRESSION_WORDS = [
    "happy", "excited", "beautiful", "wonderful", "interesting",
    "favorite", "favourite", "great", "delicious", "friendly", "amazing",
]


def english_genres_for_grade(grade: str) -> list[str]:
    return [genre for genre, tpl in ENGLISH_TEMPLATES.items() if grade in tpl["grades"]]
