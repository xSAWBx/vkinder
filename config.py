import psycopg2

community_token = 'vk1.a.AgtUQuSUnoXVWjJjnbBouJ3u1871Ic8c-xw5phHcE9Jm9cgYlbBGfHn1yQazR84aD-WcNOofftvgDyE23CtV1kkv4WBj6qlKwdqD0hYYT3R9CNWJnqwbf41-STeHJHSGqouQS8wbnf2m4j4_j_0i9VglHdskV-6kumRNfjDkqxPQQUrlKsnPT-jAkDaxHGpUfxqJXNEDXTwHM9cB4JA77Q'
access_token = 'vk1.a.SoZGz5gGFyef6Kpm9hwpb5Wx3082n0bSuZ9kQlsKAdnUIxz_9IGkcpEY6M_F8TI4NpadYkEVoStrD-NLiHB0IINJC5BWqDYa2t4mhTfo-g6MGVhOwmmrcS6JDm5vBCyDiB4pXOWzdxRKB_bfB16W_3orTj1clrTCTGsVRhTJDZ7Qs6YvcJcuIqkdpCyfdlNI-EbRqlSYeZam-4qf9K6tAg'


db_url_object = "postgresql+psycopg2://student:student@localhost/student_diplom"





# https://oauth.vk.com/authorize?client_id=51692326&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,photos,offline,wall&response_type=token&v=5.131

# https://oauth.vk.com/authorize?client_id=51692326&redirect_uri=https://api.vk.com/blank.html&scope=offline,wall,photos&response_type=token

# https://api.vk.com/blank.html#access_token=vk1.a.SoZGz5gGFyef6Kpm9hwpb5Wx3082n0bSuZ9kQlsKAdnUIxz_9IGkcpEY6M_F8TI4NpadYkEVoStrD-NLiHB0IINJC5BWqDYa2t4mhTfo-g6MGVhOwmmrcS6JDm5vBCyDiB4pXOWzdxRKB_bfB16W_3orTj1clrTCTGsVRhTJDZ7Qs6YvcJcuIqkdpCyfdlNI-EbRqlSYeZam-4qf9K6tAg&expires_in=0&user_id=757119831