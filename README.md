## Preface
Actually, this is a freelance project and it should not be publicly available so that all sorts of "advanced programmers" (*beginners*) do not make their corrections, and then ask what is wrong.

## How to use this (**not shit**)
This bot is extremely easy to use. Initially, you need to run the program itself (the main file), and then insert your data into the created files. For example:

parameters.toml
```
admin=[your_vk_id]
group_id=yout_group_vk_id
count=0
city="Your city (for example: Moscow)"
```

config.py
```Python
vk_token = 'Your VK token'
ddt_token = 'Your Dadata token'
qiwi_token = 'Your Qiwi token'
```

## Making money!
There are 2 payment methods in the bot (one of them is temporarily unavailable):
- Via VK Pay
- Via Qiwi P2P

In the first case, we only need to log in via the passport in VKPay, in the second case, in addition to authorization, you will also need to get a p2p qiwi token to continue working and, accordingly, insert it into ```config.py ```

### Links!
[Get Dadata token](https://dadata.ru/api/)
[Get Qiwi P2P (**!!!**) token](https://qiwi.com/p2p-admin/api)

<blockquote> In addition to the P2P token, Qiwi also has a regular API access token, I pointed to the right link (sometimes it does not respond) </blockquote>