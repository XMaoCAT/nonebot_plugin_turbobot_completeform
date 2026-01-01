from datetime import datetime, timedelta
import html
import base64

import httpx
from nonebot import on_command, on_fullmatch
from nonebot.adapters.onebot.v11 import Message, MessageEvent, GroupMessageEvent, Bot, MessageSegment
from nonebot.params import CommandArg, ArgStr
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from nonebot.typing import T_State

from .config import Config
from .libraries.db_utils import bind_user, get_bot_key, is_already_bound, unbind_user
from .permission.models import UserPermission


def _check_group() -> Rule:
    """群组授权检查"""
    async def _checker(event: MessageEvent) -> bool:
        if not Config.allowed_groups:
            return True  # 空列表允许所有
        if isinstance(event, GroupMessageEvent):
            return event.group_id in Config.allowed_groups
        return True  # 私聊允许
    return Rule(_checker)


group_rule = _check_group()

__plugin_meta__ = PluginMetadata(
    name="turbo",
    description="给turbo用户提供指令服务的插件",
    usage="",
    type="application",
    extra={},
)

help = on_command('tbhelp', aliases={'帮助'}, priority=5, rule=group_rule)
set_name = on_command('setName', aliases={'setname', '设置名称', '修改名称'}, priority=5, rule=group_rule)
reset_name = on_command('resetName', aliases={'resetname', '重置名称', '删除名称'}, priority=5, rule=group_rule)
show_name = on_command('name', aliases={'showName', '查询名称', '查看名称'}, priority=5, rule=group_rule)
set_ticket = on_command('setTicket', aliases={'setticket', '设置票', '锁定票'}, priority=5, rule=group_rule)
reset_ticket = on_command('resetTicket', aliases={'resetticket', '重置票', '取消票'}, priority=5, rule=group_rule)
show_ticket = on_command('ticket', aliases={'showTicket', '查询票', '查看票'}, priority=5, rule=group_rule)
bind = on_command('bind', aliases={'绑定'}, priority=5, rule=group_rule)
unbind = on_command('unbind', aliases={'解绑'}, priority=5, rule=group_rule)
network = on_command('network', aliases={'网络状态', '查询网络'}, priority=5, rule=group_rule)
network_keyword = on_fullmatch(('舞萌状态', '舞萌活着吗'), priority=5, rule=group_rule)
show_permission = on_command('showPermission', aliases={'permission', '获取权限', '展示权限', '权限', '权限查询'}, priority=5, rule=group_rule)
show_friends = on_command('showFriends', aliases={'showfriends', 'friends', 'friendslist','好友', '好友列表', '查询好友', '查看好友'}, priority=5, rule=group_rule)
show_friend_requests = on_command('showFriendRequests', aliases={'showfriendrequests', '好友请求', '好友请求列表', '查询好友请求'}, priority=5, rule=group_rule)
add_friend = on_command('addFriend', aliases={'addfriend', 'add', '加好友', '添加好友', '好友添加'}, priority=5, rule=group_rule)
accept_friend = on_command('acceptFriend', aliases={'acceptfriend', 'accept', '同意好友', '同意好友申请', '同意好友请求', '接受好友请求'}, priority=5, rule=group_rule)
deny_friend = on_command('denyFriend', aliases={'denyfriend', 'deny', '拒绝好友', '拒绝好友请求', '拒绝好友申请'}, priority=5, rule=group_rule)
remove_friend = on_command('removeFriend', aliases={'removefriend', 'remove', '删除好友', '移除好友'}, priority=5, rule=group_rule)
arcade_info_detail = on_command('arcadeInfo', aliases={'arcadeinfo', 'info', 'arcade', '机厅', '查卡', '机厅信息'}, rule=group_rule)
arcade_wanji = on_fullmatch('万几', priority=5, rule=group_rule)

# === 新增功能命令定义 ===
show_user = on_command('user', aliases={'showUser', '用户信息', '查询用户', '我的信息'}, priority=5, rule=group_rule)
show_network_status = on_command('networkStatus', aliases={'机厅状态', '机厅网络', '查询机厅状态'}, priority=5, rule=group_rule)
show_records = on_command('records', aliases={'历史记录', '游玩记录', '查询记录'}, priority=5, rule=group_rule)
show_user_settings = on_command('showSettings', aliases={'settings', '查看设置', '显示设置', '用户设置'}, priority=5, rule=group_rule)
set_user_settings = on_command('setSettings', aliases={'设置', '修改设置'}, priority=5, rule=group_rule)
set_avatar = on_command('setAvatar', aliases={'setavatar', '设置头像', '修改头像'}, priority=5, rule=group_rule)
reset_avatar = on_command('resetAvatar', aliases={'resetavatar', '重置头像', '删除头像'}, priority=5, rule=group_rule)
set_friend_search_policy = on_command('setSearchPolicy', aliases={'setsearchpolicy', '设置好友查找', '好友查找设置'}, priority=5, rule=group_rule)
show_rivals = on_command('showRivals', aliases={'showrivals', 'rivals', '对手', '对手列表', '查询对手', '查看对手'}, priority=5, rule=group_rule)
add_rival = on_command('addRival', aliases={'addrival', '添加对手', '加对手'}, priority=5, rule=group_rule)
remove_rival = on_command('removeRival', aliases={'removerival', '删除对手', '移除对手'}, priority=5, rule=group_rule)

@help.handle()
async def handle_help(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_help()
    @Description: 输出所有指令的帮助信息
    @Param {MessageEvent} event: 消息事件
    """
    
    help_message = """
指令帮助信息：

【基础功能】
1. /bind 或 /绑定 - 绑定您的Turbo账号
2. /unbind 或 /解绑 - 解绑您的Turbo账号
3. /user 或 /用户信息 - 查看个人信息
4. /showPermission 或 /权限查询 - 显示您的权限信息

【名称管理】
5. /setName 或 /设置名称 - 设置您的名称
6. /resetName 或 /重置名称 - 重置您的名称
7. /name 或 /查询名称 - 查看当前名称

【头像管理】
8. /setAvatar 或 /设置头像 - 设置头像
9. /resetAvatar 或 /重置头像 - 重置头像

【功能票】
10. /setTicket 或 /设置票 - 锁定功能票
11. /resetTicket 或 /重置票 - 重置功能票
12. /ticket 或 /查询票 - 查看功能票状态

【网络与机厅】
13. /network 或 /网络状态 - 查看当前网络状态
14. /networkStatus 或 /机厅状态 - 查询机厅网络状态
15. /info 或 /机厅 - 查询机厅信息

【历史记录】
16. /records 或 /历史记录 - 查询游玩记录

【用户设置】
17. /showSettings 或 /查看设置 - 查看用户设置
18. /setSettings 或 /修改设置 - 修改用户设置
19. /setSearchPolicy 或 /设置好友查找 - 设置好友查找策略

【好友系统】
20. /showFriends 或 /好友列表 - 查看好友列表
21. /showFriendRequests 或 /好友请求 - 查看好友请求
22. /addFriend 或 /添加好友 - 添加好友
23. /acceptFriend 或 /同意好友 - 接受好友请求
24. /denyFriend 或 /拒绝好友 - 拒绝好友请求
25. /removeFriend 或 /删除好友 - 删除好友

【对手系统】
26. /showRivals 或 /对手列表 - 查看对手列表
27. /addRival 或 /添加对手 - 添加对手
28. /removeRival 或 /删除对手 - 删除对手
    """
    
    await help.send(help_message)


@bind.handle()
async def handle_bind(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_bind()
    @Description: 处理用户绑定操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 命令参数
    """
    arg_str = str(arg).strip()
    
    # help 功能
    if arg_str.lower() == 'help':
        help_text = """【/bind 绑定账号】
用法：/bind <botToken>
别名：/绑定

参数说明：
  botToken - 您的Turbo机器人令牌（必填）

功能：将您的QQ与Turbo账号进行绑定，绑定后可使用所有功能。

API接口：POST /bot/bind
请求体：{"botToken": "string", "botName": "string"}

示例：/bind abc123xyz

注意：发送的消息将自动撤回以保护您的隐私。"""
        await bind.send(help_text)
        return
    
    # 尝试撤回用户消息保护隐私
    try:
        await bot.delete_msg(message_id=event.message_id)
    except Exception:
        pass

    qqid = str(event.get_user_id())
    bot_token = arg_str

    if not bot_token:
        await bind.send("绑定命令后需要包含botToken。")
        return
    if is_already_bound(qqid):
        await bind.send("您已经绑定过一个bot_token，无需重复绑定。")
        return

    payload = {"botToken": bot_token, "botName": Config.bot_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/bot/bind', json=payload)

        if response.status_code == 200:
            try:
                response_data = response.json()
                bot_key = response_data["botKey"]
                bind_user(qqid, bot_token, bot_key)
                await bind.send("绑定成功！")
            except Exception:
                await bind.send(f"绑定失败，服务器返回数据异常：{response.text[:100]}")
        else:
            await bind.send(f"绑定失败，HTTP响应状态码为{response.status_code}，响应：{response.text[:100]}")
    except Exception as e:
        await bind.send(f"绑定过程中出现错误：{e}")


@unbind.handle()
async def handle_unbind(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_unbind()
    @Description: 处理用户解绑操作
    @Param {MessageEvent} event: 消息事件
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/unbind 解绑账号】
用法：/unbind
别名：/解绑

功能：解除当前QQ与Turbo账号的绑定关系。

API接口：POST /bot/unbind
请求体：{"botKey": "string"}

注意：解绑后需要重新绑定才能使用相关功能。"""
        await unbind.send(help_text)
        return
    
    qqid = str(event.get_user_id())
    if not is_already_bound(qqid):
        await unbind.send("您还未绑定bot，无法解绑！")
        return
    bot_key = get_bot_key(qqid)
    payload = {"botKey": bot_key}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/bot/unbind', json=payload)

        if response.status_code == 200:
            unbind_user(qqid)
            await unbind.send("解绑成功！")
        else:
            await unbind.send(f"解绑失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await unbind.send(f"解绑过程中出现错误：{e}")


@set_name.handle()
async def handle_set_name(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_set_name()
    @Description: 处理用户修改maimai名称操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 命令参数
    """
    new_name = str(arg).strip()
    
    # help 功能
    if new_name.lower() == 'help':
        help_text = """【/setName 设置名称】
用法：/setName <maimaiName>
别名：/setname, /设置名称, /修改名称

参数说明：
  maimaiName - 要设置的新名称（必填，string类型）

功能：设置您在maimai中显示的名称。

API接口：POST /web/setMaimaiName
请求体：{"maimaiName": "string"}

示例：/setName 我的新名字"""
        await set_name.send(help_text)
        return
    
    qqid = str(event.get_user_id())

    if not new_name:
        await set_name.send("修改名称命令后需要包含新的名称。")
        return

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await set_name.send("您尚未绑定，请先使用/bind 指令绑定。")
        return

    payload = {"maimaiName": new_name}

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{Config.api_base_url}/web/setMaimaiName', json=payload, headers=headers
            )

        if response.status_code == 200:
            await set_name.send("名称修改成功！")
        elif response.status_code == 400:
            await set_name.send("修改名称失败，验证码验证失败或数据不合法。")
        elif response.status_code == 401:
            await set_name.send("请求的Token缺失或不合法，请检查权限。")
        elif response.status_code == 403:
            await set_name.send("权限不足，无法修改名称。")
        elif response.status_code == 410:
            await set_name.send("该用户已被封禁，请联系管理员。")
        elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await set_name.send(f"{error_message}")
        else:
            await set_name.send(f"修改名称失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await set_name.send(f"修改名称过程中出现错误：{e}")



@reset_name.handle()
async def handle_reset_name(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_reset_name()
    @Description: 处理用户重置名称操作
    @Param {MessageEvent} event: 消息事件
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/resetName 重置名称】
用法：/resetName
别名：/resetname, /重置名称, /删除名称

功能：将您的maimai名称重置为默认状态。

API接口：POST /web/resetMaimaiName
无需请求体参数"""
        await reset_name.send(help_text)
        return
    
    qqid = str(event.get_user_id())

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await reset_name.send("您尚未绑定，请先使用/bind 指令绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/web/resetMaimaiName', headers=headers)

        if response.status_code == 200:
            await reset_name.send("名称重置成功！")
        elif response.status_code == 400:
            await reset_name.send("重置名称失败，验证码验证失败或数据不合法。")
        elif response.status_code == 401:
            await reset_name.send("请求的Token缺失或不合法，请检查权限。")
        elif response.status_code == 403:
            await reset_name.send("权限不足，无法重置名称。")
        elif response.status_code == 410:
            await reset_name.send("该用户已被封禁，请联系管理员。")
        elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await reset_name.send(f"{error_message}")
        else:
            await reset_name.send(f"重置名称失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await reset_name.send(f"重置名称过程中出现错误：{e}")

@show_name.handle()
async def handle_show_name(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_name()
    @Description: 处理用户查询当前名称操作
    @Param {MessageEvent} event: 消息事件
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/name 查询名称】
用法：/name
别名：/showName, /查询名称, /查看名称

功能：查看您当前设置的maimai名称。

API接口：GET /web/showMaimaiName
无需请求参数"""
        await show_name.send(help_text)
        return

    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await show_name.send("您尚未绑定，请先绑定。")
        return

    headers = {
        "Authorization": f"BotKey {bot_key}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/web/showMaimaiName', headers=headers)

            if response.status_code == 200:
                current_name = response.text
                await show_name.send(f"您当前的ID为：{current_name}")
            elif response.status_code == 400:
                await show_name.send("请求数据不合法，请检查请求。")
            elif response.status_code == 401:
                await show_name.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_name.send("权限不足，无法获取当前ID。")
            elif response.status_code == 410:
                await show_name.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_name.send(f"{error_message}")
            else:
                await show_name.send(f"获取ID失败，HTTP响应状态码为：{response.status_code}。")
    except Exception as e:
        await show_name.send(f"获取ID过程中出现错误：{e}")



@set_ticket.handle()
async def handle_set_ticket(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_set_ticket()
    @Description: 处理用户设置锁定功能票操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 命令参数
    """
    ticket_id_str = str(arg).strip()
    
    # help 功能
    if ticket_id_str.lower() == 'help':
        help_text = """【/setTicket 设置功能票】
用法：/setTicket <ticketId>
别名：/setticket, /设置票, /锁定票

参数说明：
  ticketId - 票ID（必填，Int类型）

常见票ID：
  2-6: 付费2-6倍票
  10005/10105/10205: 活动5倍票
  11001-11005: 免费票（1.5-5倍）
  30001: 特殊2倍票

功能：锁定指定的功能票，每次游玩时自动使用。

API接口：POST /web/setTickets
请求体：{"ticketId": Int}

示例：/setTicket 3"""
        await set_ticket.send(help_text)
        return
    
    qqid = str(event.get_user_id())

    if not ticket_id_str.isdigit():
        await set_ticket.send("设置票的命令后需要跟一个数字作为ticketId。")
        return

    ticket_id = int(ticket_id_str)

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await set_ticket.send("您尚未绑定，请先绑定。")
        return

    payload = {"ticketId": ticket_id}

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{Config.api_base_url}/web/setTickets', json=payload, headers=headers
            )

        if response.status_code == 200:
            ticket_description = get_ticket_description(ticket_id)
            await set_ticket.send(f"用户功能票成功锁定为：{ticket_description}")
        elif response.status_code == 400:
            await set_ticket.send("设置票失败，验证码验证失败或数据不合法。")
        elif response.status_code == 401:
            await set_ticket.send("请求的Token缺失或不合法，请检查权限。")
        elif response.status_code == 403:
            await set_ticket.send("权限不足，无法设置票。")
        elif response.status_code == 410:
            await set_ticket.send("该用户已被封禁，请联系管理员。")
        elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await set_ticket.send(f"{error_message}")
        else:
            await set_ticket.send(f"设置票失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await set_ticket.send(f"设置票过程中出现错误：{e}")



@reset_ticket.handle()
async def handle_reset_ticket(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_reset_ticket()
    @Description: 处理用户取消锁定功能票操作
    @Param {MessageEvent} event: 消息事件
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/resetTicket 重置功能票】
用法：/resetTicket
别名：/resetticket, /重置票, /取消票

功能：取消当前锁定的功能票，恢复正常游玩模式。

API接口：POST /web/resetTickets
无需请求体参数"""
        await reset_ticket.send(help_text)
        return
    
    qqid = str(event.get_user_id())

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await reset_ticket.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{Config.api_base_url}/web/resetTickets', headers=headers
            )

        if response.status_code == 200:
            await reset_ticket.send("用户功能票取消锁定成功！")
        elif response.status_code == 400:
            await reset_ticket.send("取消票失败，验证码验证失败或数据不合法。")
        elif response.status_code == 401:
            await reset_ticket.send("请求的Token缺失或不合法，请检查权限。")
        elif response.status_code == 403:
            await reset_ticket.send("权限不足，无法取消票。")
        elif response.status_code == 410:
            await reset_ticket.send("该用户已被封禁，请联系管理员。")
        elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await reset_ticket.send(f"{error_message}")
        else:
            await reset_ticket.send(f"取消票失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await reset_ticket.send(f"取消票过程中出现错误：{e}")

@show_ticket.handle()
async def handle_show_ticket(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_ticket()
    @Description: 处理用户查询当前功能票信息操作
    @Param {MessageEvent} event: 消息事件
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/ticket 查询功能票】
用法：/ticket
别名：/showTicket, /查询票, /查看票

功能：查看当前锁定的功能票以及账号内的票库存。

API接口：GET /web/currentTickets
无需请求参数

返回信息包括：
  - 当前锁定的票类型
  - 各类型票的库存数量"""
        await show_ticket.send(help_text)
        return

    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await show_ticket.send("您尚未绑定，请先绑定。")
        return

    headers = {
        "Authorization": f"BotKey {bot_key}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/web/currentTickets', headers=headers)

            if response.status_code == 200:
                ticket_data = response.json()

                turbo_ticket = ticket_data.get("turboTicket", {})
                is_enable = turbo_ticket.get("isEnable", False)
                ticket_id = turbo_ticket.get("ticketId", 0)

                if is_enable:
                    ticket_description = get_ticket_description(ticket_id)
                    message = f"已启用功能票锁定，当前锁定功能票为：{ticket_description}\n"
                else:
                    message = "未启用功能票锁定\n"

                maimai_tickets = ticket_data.get("maimaiTickets", [])
                available_tickets = []

                for ticket in maimai_tickets:
                    stock = ticket.get("stock", 0)
                    if stock > 0:
                        ticket_desc = get_ticket_description(ticket.get("ticketId", 0))
                        available_tickets.append(f"{ticket_desc}：{stock}张")

                if available_tickets:
                    message += "\n账号内功能票库存：\n" + "\n".join(available_tickets)

                await show_ticket.send(message)
            elif response.status_code == 400:
                await show_ticket.send("请求数据不合法，请检查请求。")
            elif response.status_code == 401:
                await show_ticket.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_ticket.send("权限不足，无法获取功能票信息。")
            elif response.status_code == 410:
                await show_ticket.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_ticket.send(f"{error_message}")
            else:
                await show_ticket.send(f"获取功能票信息失败，HTTP响应状态码为：{response.status_code}。")
    except Exception as e:
        await show_ticket.send(f"获取功能票信息过程中出现错误：{e}")


@network.handle()
@network_keyword.handle()
async def handle_network(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_network()
    @Description: 处理获取网络相关信息的操作
    @Param {Event} event: 事件信息
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/network 网络状态】
用法：/network
别名：/网络状态, /查询网络, 舞萌状态, 舞萌活着吗

功能：查看当前服务器网络请求统计信息。

API接口：GET /web/showServerRequests
无需请求参数

返回信息包括：
  - 一小时内总请求数
  - 异常请求数和占比
  - Z-LIB压缩跳过数
  - 重试/失败请求数
  - 小黑屋预估概率"""
        await network.send(help_text)
        return

    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)
    
    if not bot_key:
        await network.send("您尚未绑定，请先绑定。")
        return

    headers = {
        "Authorization": f"BotKey {bot_key}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response_network = await client.get(f'{Config.api_base_url}/web/showServerRequests', headers=headers)

            if response_network.status_code == 200:
                network_data = response_network.json()

                if network_data:
                    all_requests_count = network_data.get("requestsCount", 0)
                    exception_requests_count = network_data.get("exceptionRequestsCount", 0)
                    zlib_skipped_requests_count = network_data.get("zlibSkippedRequestsCount", 0)
                    retry_requests_count = network_data.get("retryRequestsCount", 0)
                    panic_requests_count = network_data.get("panicRequestsCount", 0)
                    exception_requests_rate = network_data.get("exceptionRequestsRate", 0)
                    black_room_probability = 1 - (1 - exception_requests_rate / 100) ** 10

                    message = (
                        f"\n一小时内总请求数：{all_requests_count}\n"
                        f"异常请求数：{exception_requests_count}\n"
                        f"异常请求占比：{exception_requests_rate:.2f}%\n"
                        f"Z-LIB 跳过数量：{zlib_skipped_requests_count}\n"
                        f"重试请求数：{retry_requests_count}\n"
                        f"失败请求数：{panic_requests_count}\n\n"
                        f"10pc至少有一次小黑屋的预估概率：{black_room_probability:.2%}\n\n"
                    )
                    message += (
                        "响应数据的「Z-LIB」压缩跳过率与请求重试次数可以反应当前网络情况。\n"
                        "压缩跳过率超过「3%」时，可能会出现网络不稳定现象。\n"
                        "请求重试率和失败率较高时，网络或服务器可能存在问题。\n"
                        "小黑屋率为使用一小时异常率估算的数据，仅供参考。"
                    )

                    await network.send(message)
                else:
                    await network.send("获取网络数据失败。")
            elif response_network.status_code == 400:
                await network.send("请求数据不合法，请检查请求。")
            elif response_network.status_code == 401:
                await network.send("请求的Token缺失或不合法，请检查权限。")
            elif response_network.status_code == 403:
                await network.send("权限不足，无法获取网络数据。")
            elif response_network.status_code == 410:
                await network.send("该用户已被封禁，请联系管理员。")
            elif response_network.status_code == 500:
                error_message = response_network.json().get("message", "服务器内部错误")
                await network.send(f"{error_message}")
            else:
                await network.send(f"获取数据失败，HTTP响应状态码为：{response_network.status_code}。")
    except Exception as e:
        await network.send(f"获取数据过程中出现错误：{e}")


@show_permission.handle()
async def handle_show_permission(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_permission()
    @Description: 处理用户获取权限操作
    @Param {MessageEvent} event: 消息事件
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/showPermission 权限查询】
用法：/showPermission
别名：/permission, /获取权限, /展示权限, /权限, /权限查询

功能：查看您当前的权限级别和已授予的详细权限。

API接口：
  GET /permission/showPermission
  GET /web/showTurboPermission"""
        await show_permission.send(help_text)
        return
    
    qqid = str(event.get_user_id())

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await show_permission.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/permission/showPermission', headers=headers)

            if response.status_code == 200:
                permission_text = response.text.strip().replace('"', '')
                response_data = UserPermission(permission=permission_text)
                permission_level = response_data.get_permission_level()
                message = f"用户权限级别：{permission_level}\n"
            elif response.status_code == 400:
                await show_permission.send("请求数据不合法，请检查请求。")
                return
            elif response.status_code == 401:
                await show_permission.send("请求的Token缺失或不合法，请检查权限。")
                return
            elif response.status_code == 403:
                await show_permission.send("权限不足，无法获取权限信息。")
                return
            elif response.status_code == 410:
                await show_permission.send("该用户已被封禁，请联系管理员。")
                return
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_permission.send(f"{error_message}")
                return
            else:
                await show_permission.send(f"获取权限信息失败，HTTP响应状态码为 {response.status_code}。")
                return

            response_turbo = await client.get(f'{Config.api_base_url}/web/showTurboPermission', headers=headers)

            if response_turbo.status_code == 200:
                turbo_permissions = response_turbo.json()
                if turbo_permissions:
                    granted_permissions = []
                    for permission in turbo_permissions:
                        description = permission.get("permissionDescription", "未知权限")
                        is_granted = permission.get("isGranted", False)
                        if is_granted:
                            description = html.unescape(description)
                            granted_permissions.append(description)

                    if granted_permissions:
                        message += "\n已授予的详细权限：\n" + "\n".join(granted_permissions)
                    else:
                        message += "\n未授予任何详细权限。"
                else:
                    message += "\n无法获取详细权限信息。"
            elif response_turbo.status_code == 400:
                message += "\n请求数据不合法，请检查请求。"
            elif response_turbo.status_code == 401:
                message += "\n请求的Token缺失或不合法，请检查权限。"
            elif response_turbo.status_code == 403:
                message += "\n权限不足，无法获取详细Turbo权限信息。"
            elif response_turbo.status_code == 410:
                message += "\n该用户已被封禁，请联系管理员。"
            elif response_turbo.status_code == 500:
                error_message = response_turbo.json().get("message", "服务器内部错误")
                message += f"\n{error_message}"
            else:
                message += f"\n获取详细Turbo权限失败，HTTP响应状态码为 {response_turbo.status_code}。"

            await show_permission.send(message)

    except Exception as e:
        await show_permission.send(f"获取用户权限过程中出现错误：{e}")

@show_friends.handle()
async def handle_show_friends(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_friends()
    @Description: 处理用户获取好友列表操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 命令参数（可选）
    """
    page_str = str(arg).strip()
    
    # help 功能
    if page_str.lower() == 'help':
        help_text = """【/showFriends 好友列表】
用法：/showFriends [页码]
别名：/showfriends, /friends, /friendslist, /好友, /好友列表, /查询好友, /查看好友

参数说明：
  页码 - 可选，默认为1（Int类型）

功能：查看您的好友列表，支持分页显示。

API接口：GET /web/showFriends
查询参数：page (Int)

示例：/showFriends 2"""
        await show_friends.send(help_text)
        return

    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)
    
    if page_str.isdigit():
        page = int(page_str)
    else:
        page = 1

    if not bot_key:
        await show_friends.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/web/showFriends', params={"page": page}, headers=headers)

            if response.status_code == 200:
                friends_data = response.json()

                content = friends_data.get("content", [])
                total_elements = friends_data.get("totalElements", 0)
                total_pages = friends_data.get("totalPages", 0)

                if not content:
                    await show_friends.send("您目前还没有添加好友。")
                    return

                friend_names = [friend["turboName"] for friend in content]
                friend_list_message = "好友列表：\n" + "\n".join(friend_names)

                message = (
                    f"{friend_list_message}\n\n"
                    f"共 {total_elements} 位好友，当前 {page}/{total_pages} 页。"
                )

                if total_pages > 1:
                    message += "\n可以在命令后添加页数查看对应页数的好友。"

                await show_friends.send(message)

            elif response.status_code == 400:
                await show_friends.send("请求数据不合法，请检查请求。")
            elif response.status_code == 401:
                await show_friends.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_friends.send("权限不足，无法获取好友列表。")
            elif response.status_code == 410:
                await show_friends.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_friends.send(f"{error_message}")
            else:
                await show_friends.send(f"获取好友列表失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await show_friends.send(f"获取好友列表过程中出现错误：{e}")

@show_friend_requests.handle()
async def handle_show_friend_requests(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_friend_requests()
    @Description: 处理用户获取好友请求操作
    @Param {MessageEvent} event: 消息事件
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/showFriendRequests 好友请求】
用法：/showFriendRequests
别名：/showfriendrequests, /好友请求, /好友请求列表, /查询好友请求

功能：查看待处理的好友请求列表。

API接口：GET /web/showFriendRequests
无需请求参数

返回信息包括：
  - 请求者名称
  - 请求时间"""
        await show_friend_requests.send(help_text)
        return

    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await show_friend_requests.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/web/showFriendRequests', headers=headers)

            if response.status_code == 200:
                friend_requests = response.json()

                if not friend_requests:
                    await show_friend_requests.send("当前没有待处理的好友请求。")
                    return

                requests_message = "好友请求列表：\n"
                for request in friend_requests:
                    turbo_name = request.get("turboName", "未知用户")
                    request_time = request.get("requestTime", "")

                    try:
                        formatted_time = datetime.strptime(request_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y/%m/%d %H:%M:%S")
                    except ValueError:
                        formatted_time = request_time

                    requests_message += f"{turbo_name} - 请求时间：{formatted_time}\n"

                await show_friend_requests.send(requests_message)

            elif response.status_code == 400:
                await show_friend_requests.send("请求数据不合法，请检查请求。")
            elif response.status_code == 401:
                await show_friend_requests.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_friend_requests.send("权限不足，无法获取好友请求。")
            elif response.status_code == 410:
                await show_friend_requests.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_friend_requests.send(f"{error_message}")
            else:
                await show_friend_requests.send(f"获取好友请求失败，HTTP响应状态码为 {response.status_code}。")

    except Exception as e:
        await show_friend_requests.send(f"获取好友请求过程中出现错误：{e}")

@add_friend.handle()
async def handle_add_friend(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_add_friend()
    @Description: 处理用户添加好友操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 用户输入的好友名称
    """
    turbo_name = str(arg).strip()
    
    # help 功能
    if turbo_name.lower() == 'help':
        help_text = """【/addFriend 添加好友】
用法：/addFriend <turboName>
别名：/addfriend, /add, /加好友, /添加好友, /好友添加

参数说明：
  turboName - 要添加的好友名称（必填，string类型）

功能：向指定用户发送好友请求。

API接口：POST /web/addFriend
请求体：{"turboName": "string"}

示例：/addFriend 张三"""
        await add_friend.send(help_text)
        return

    qqid = str(event.get_user_id())

    if not turbo_name:
        await add_friend.send("请提供要添加好友的名称。")
        return

    bot_key = get_bot_key(qqid)

    if not bot_key:
        await add_friend.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"turboName": turbo_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/web/addFriend', json=payload, headers=headers)

            if response.status_code == 200:
                await add_friend.send(f"好友请求已发送给：{turbo_name}")
            elif response.status_code == 400:
                await add_friend.send("请求数据不合法，请检查输入的好友名称。")
            elif response.status_code == 401:
                await add_friend.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await add_friend.send("权限不足，无法添加好友。")
            elif response.status_code == 410:
                await add_friend.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await add_friend.send(f"{error_message}")
            else:
                await add_friend.send(f"添加好友失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await add_friend.send(f"添加好友过程中出现错误：{e}")

@accept_friend.handle()
async def handle_accept_friend(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_accept_friend()
    @Description: 处理用户接受好友请求操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 用户输入的好友名称
    """
    turbo_name = str(arg).strip()
    
    # help 功能
    if turbo_name.lower() == 'help':
        help_text = """【/acceptFriend 同意好友】
用法：/acceptFriend <turboName>
别名：/acceptfriend, /accept, /同意好友, /同意好友申请, /同意好友请求, /接受好友请求

参数说明：
  turboName - 要接受的好友名称（必填，string类型）

功能：接受指定用户的好友请求。

API接口：POST /web/acceptFriend
请求体：{"turboName": "string"}

示例：/acceptFriend 李四"""
        await accept_friend.send(help_text)
        return

    qqid = str(event.get_user_id())

    if not turbo_name:
        await accept_friend.send("请提供要接受好友请求的名称。")
        return

    bot_key = get_bot_key(qqid)

    if not bot_key:
        await accept_friend.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"turboName": turbo_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/web/acceptFriend', json=payload, headers=headers)

            if response.status_code == 200:
                await accept_friend.send(f"您已接受 {turbo_name} 的好友请求。")
            elif response.status_code == 400:
                await accept_friend.send("请求数据不合法，请检查输入的好友名称。")
            elif response.status_code == 401:
                await accept_friend.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await accept_friend.send("权限不足，无法接受好友请求。")
            elif response.status_code == 410:
                await accept_friend.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await accept_friend.send(f"{error_message}")
            else:
                await accept_friend.send(f"接受好友请求失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await accept_friend.send(f"接受好友请求过程中出现错误：{e}")

@deny_friend.handle()
async def handle_deny_friend(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_deny_friend()
    @Description: 处理用户拒绝好友请求操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 用户输入的好友名称
    """
    turbo_name = str(arg).strip()
    
    # help 功能
    if turbo_name.lower() == 'help':
        help_text = """【/denyFriend 拒绝好友】
用法：/denyFriend <turboName>
别名：/denyfriend, /deny, /拒绝好友, /拒绝好友请求, /拒绝好友申请

参数说明：
  turboName - 要拒绝的好友名称（必填，string类型）

功能：拒绝指定用户的好友请求。

API接口：POST /web/denyFriend
请求体：{"turboName": "string"}

示例：/denyFriend 王五"""
        await deny_friend.send(help_text)
        return

    qqid = str(event.get_user_id())

    if not turbo_name:
        await deny_friend.send("请提供要拒绝的好友请求的名称。")
        return

    bot_key = get_bot_key(qqid)

    if not bot_key:
        await deny_friend.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"turboName": turbo_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/web/denyFriend', json=payload, headers=headers)

            if response.status_code == 200:
                await deny_friend.send(f"您已拒绝 {turbo_name} 的好友请求。")
            elif response.status_code == 400:
                await deny_friend.send("请求数据不合法，请检查输入的好友名称。")
            elif response.status_code == 401:
                await deny_friend.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await deny_friend.send("权限不足，无法拒绝好友请求。")
            elif response.status_code == 410:
                await deny_friend.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await deny_friend.send(f"{error_message}")
            else:
                await deny_friend.send(f"拒绝好友请求失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await deny_friend.send(f"拒绝好友请求过程中出现错误：{e}")

@remove_friend.handle()
async def handle_remove_friend(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_remove_friend()
    @Description: 处理用户删除好友操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 用户输入的好友名称
    """
    turbo_name = str(arg).strip()
    
    # help 功能
    if turbo_name.lower() == 'help':
        help_text = """【/removeFriend 删除好友】
用法：/removeFriend <turboName>
别名：/removefriend, /remove, /删除好友, /移除好友

参数说明：
  turboName - 要删除的好友名称（必填，string类型）

功能：删除指定的好友。

API接口：POST /web/removeFriend
请求体：{"turboName": "string"}

示例：/removeFriend 赵六"""
        await remove_friend.send(help_text)
        return

    qqid = str(event.get_user_id())

    if not turbo_name:
        await remove_friend.send("请提供要删除的好友名称。")
        return

    bot_key = get_bot_key(qqid)

    if not bot_key:
        await remove_friend.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"turboName": turbo_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/web/removeFriend', json=payload, headers=headers)

            if response.status_code == 200:
                await remove_friend.send(f"您已成功删除好友：{turbo_name}")
            elif response.status_code == 400:
                await remove_friend.send("请求数据不合法，请检查输入的好友名称。")
            elif response.status_code == 401:
                await remove_friend.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await remove_friend.send("权限不足，无法删除好友。")
            elif response.status_code == 410:
                await remove_friend.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await remove_friend.send(f"{error_message}")
            else:
                await remove_friend.send(f"删除好友失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await remove_friend.send(f"删除好友过程中出现错误：{e}")

@arcade_info_detail.handle()
async def handle_arcade_info_detail(event: MessageEvent, arg: Message = CommandArg()):
    arcade_name = str(arg).strip()
    
    # help 功能
    if arcade_name.lower() == 'help':
        help_text = """【/arcadeInfo 机厅信息】
用法：/arcadeInfo <机厅名称>
别名：/arcadeinfo, /info, /arcade, /机厅, /查卡, /机厅信息

参数说明：
  机厅名称 - 要查询的机厅名称（必填，string类型）

功能：查询指定机厅的详细信息，包括玩家数、pc数、网络状态等。

API接口：GET /web/arcadeInfoDetail
查询参数：arcadeName (string)

示例：/arcadeInfo 万达"""
        await arcade_info_detail.send(help_text)
        return
    
    if not arcade_name:
        await arcade_info_detail.send("请提供要查询的机厅名称。")
        return
    await _query_arcade(event, arcade_name, arcade_info_detail)


@arcade_wanji.handle()
async def handle_arcade_wanji(event: MessageEvent):
    await _query_arcade(event, "w", arcade_wanji)


async def _query_arcade(event: MessageEvent, arcade_name: str, matcher):
    """机厅查询核心逻辑"""
    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await matcher.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    params = {"arcadeName": arcade_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/web/arcadeInfoDetail', params=params, headers=headers)

            if response.status_code == 200:
                arcade_data = response.json()

                arcade_info = arcade_data.get("arcadeInfo", {})
                arcade_name_display = arcade_info.get("arcadeName", "未知机厅")
                
                # 修正错误的店铺名称
                if arcade_name_display == "黑龙江哈尔滨牡丹江万达店大玩家":
                    arcade_name_display = "牡丹江-万达大玩家 舞萌状态"
                
                thirty_minutes_player = arcade_data.get("thirtyMinutesPlayer", 0)
                one_hour_player = arcade_data.get("oneHourPlayer", 0)
                two_hours_player = arcade_data.get("twoHoursPlayer", 0)
                thirty_minutes_play_count = arcade_data.get("thirtyMinutesPlayCount", 0)
                one_hour_play_count = arcade_data.get("oneHourPlayCount", 0)
                two_hours_play_count = arcade_data.get("twoHoursPlayCount", 0)

                player_list = arcade_data.get("playerList", [])
                recent_players = [player.get("maimaiName", "未知玩家") for player in player_list[:6]]

                arcade_requested = arcade_info.get("arcadeRequested", 0)
                arcade_cached_request = arcade_info.get("arcadeCachedRequest", 0)
                arcade_fixed_request = arcade_info.get("arcadeFixedRequest", 0)
                arcade_cached_hit_rate = arcade_info.get("arcadeCachedHitRate", 0)

                cache_hit_rate = (arcade_cached_hit_rate / 100) if arcade_cached_hit_rate > 0 else 0
                error_fix_rate = (arcade_fixed_request / arcade_requested * 100) if arcade_requested > 0 else 0

                message = (
                    f"{arcade_name_display}\n\n"
                    f"30 分钟内有 {thirty_minutes_player} 名玩家，共 {thirty_minutes_play_count} pc\n"
                    f"1 小时内有 {one_hour_player} 名玩家，共 {one_hour_play_count} pc\n"
                    f"2 小时内有 {two_hours_player} 名玩家，共 {two_hours_play_count} pc\n\n"
                )

                if recent_players:
                    message += "最近游玩的 6 名玩家：\n" + "\n".join(recent_players) + "\n\n"
                else:
                    message += "最近游玩的 6 名玩家：无\n\n"

                message += (
                    f"在 {arcade_requested} 次网络请求中，缓存击中 {arcade_cached_request} 次，"
                    f"修复 {arcade_fixed_request} 次错误，缓存击中率 {cache_hit_rate:.2%}，"
                    f"缓外错误率 {error_fix_rate:.2%}"
                )

                await matcher.send(message)

            elif response.status_code == 400:
                await matcher.send("请求数据不合法，请检查机厅名称。")
            elif response.status_code == 401:
                await matcher.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await matcher.send("权限不足，无法获取机厅信息。")
            elif response.status_code == 410:
                await matcher.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await matcher.send(f"{error_message}")
            else:
                await matcher.send(f"获取机厅信息失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await matcher.send(f"获取机厅信息过程中出现错误：{e}")


def get_ticket_description(ticket_id: int) -> str:
    """
    @Author: TurboServlet
    @Func: get_ticket_description()
    @Description: 获取功能票的描述信息
    @Param {int} ticket_id: 票的ID
    @Return: str
    """
    ticket_descriptions = {
        2: '付费2倍票',
        3: '付费3倍票',
        4: '付费4倍票',
        5: '付费5倍票',
        6: '付费6倍票',
        10005: '活动5倍票 (类型1)',
        10105: '活动5倍票 (类型2)',
        10205: '活动5倍票 (类型3)',
        11001: '免费1.5倍票',
        11002: '免费2倍票',
        11003: '免费3倍票',
        11005: '免费5倍票',
        30001: '特殊2倍票',
        'default': '没有票',
    }
    return ticket_descriptions.get(ticket_id, ticket_descriptions['default'])


# === 新增功能处理函数 ===

@show_user.handle()
async def handle_show_user(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_user()
    @Description: 处理用户查询个人信息操作
    @Param {MessageEvent} event: 消息事件
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/user 用户信息】
用法：/user
别名：/showUser, /用户信息, /查询用户, /我的信息

功能：查看您的个人信息。

API接口：GET /web/user
无需请求参数

返回信息包括：
  - Turbo名称
  - 用户ID
  - 创建时间
  - 最后登录时间
  - 权限等级"""
        await show_user.send(help_text)
        return
    
    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await show_user.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/web/user', headers=headers)

            if response.status_code == 200:
                user_data = response.json()
                turbo_name = user_data.get("turboName", "未知")
                user_id = user_data.get("userId", "未知")
                create_time = user_data.get("createTime", "")
                last_login_time = user_data.get("lastLoginTime", "")
                permission = user_data.get("permission", "未知")

                try:
                    if create_time:
                        create_time = datetime.strptime(create_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y/%m/%d %H:%M:%S")
                    if last_login_time:
                        last_login_time = datetime.strptime(last_login_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y/%m/%d %H:%M:%S")
                except ValueError:
                    pass

                message = (
                    f"用户信息\n"
                    f"Turbo名称：{turbo_name}\n"
                    f"用户ID：{user_id}\n"
                    f"创建时间：{create_time}\n"
                    f"最后登录：{last_login_time}\n"
                    f"权限等级：{permission}"
                )
                await show_user.send(message)
            elif response.status_code == 401:
                await show_user.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_user.send("权限不足，无法获取用户信息。")
            elif response.status_code == 410:
                await show_user.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_user.send(f"{error_message}")
            else:
                await show_user.send(f"获取用户信息失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await show_user.send(f"获取用户信息过程中出现错误：{e}")


@show_network_status.handle()
async def handle_show_network_status(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_network_status()
    @Description: 处理获取机厅网络状态操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 机厅名称
    """
    arcade_name = str(arg).strip()
    
    # help 功能
    if arcade_name.lower() == 'help':
        help_text = """【/networkStatus 机厅网络状态】
用法：/networkStatus <机厅名称>
别名：/机厅状态, /机厅网络, /查询机厅状态

参数说明：
  机厅名称 - 要查询的机厅名称（必填，string类型）

功能：查询指定机厅的网络状态。

API接口：GET /web/showNetworkStatus
查询参数：arcadeName (string)

示例：/networkStatus 万达店"""
        await show_network_status.send(help_text)
        return

    qqid = str(event.get_user_id())

    if not arcade_name:
        await show_network_status.send("请提供要查询的机厅名称。")
        return

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await show_network_status.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    params = {"arcadeName": arcade_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/web/showNetworkStatus', params=params, headers=headers)

            if response.status_code == 200:
                status_data = response.json()
                arcade_info = status_data.get("arcadeInfo", {})
                arcade_name_display = arcade_info.get("arcadeName", arcade_name)
                network_status = status_data.get("networkStatus", "未知")
                last_update = status_data.get("lastUpdate", "")
                request_count = status_data.get("requestCount", 0)
                error_count = status_data.get("errorCount", 0)
                error_rate = status_data.get("errorRate", 0)

                try:
                    if last_update:
                        last_update = datetime.strptime(last_update, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y/%m/%d %H:%M:%S")
                except ValueError:
                    pass

                message = (
                    f"机厅：{arcade_name_display}\n"
                    f"网络状态：{network_status}\n"
                    f"最后更新：{last_update}\n"
                    f"请求数：{request_count}\n"
                    f"错误数：{error_count}\n"
                    f"错误率：{error_rate:.2f}%"
                )
                await show_network_status.send(message)
            elif response.status_code == 400:
                await show_network_status.send("请求数据不合法，请检查机厅名称。")
            elif response.status_code == 401:
                await show_network_status.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_network_status.send("权限不足，无法获取机厅状态。")
            elif response.status_code == 410:
                await show_network_status.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_network_status.send(f"{error_message}")
            else:
                await show_network_status.send(f"获取机厅状态失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await show_network_status.send(f"获取机厅状态过程中出现错误：{e}")


@show_records.handle()
async def handle_show_records(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_records()
    @Description: 处理用户查询历史记录操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 页码（可选）
    """
    page_str = str(arg).strip()
    
    # help 功能
    if page_str.lower() == 'help':
        help_text = """【/records 历史记录】
用法：/records [页码]
别名：/历史记录, /游玩记录, /查询记录

参数说明：
  页码 - 可选，默认为1（Int类型）

功能：查询您的游玩历史记录，支持分页显示。

API接口：GET /web/records
查询参数：page (Int)

示例：/records 2"""
        await show_records.send(help_text)
        return
    
    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if page_str.isdigit():
        page = int(page_str)
    else:
        page = 1

    if not bot_key:
        await show_records.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/web/records', params={"page": page}, headers=headers)

            if response.status_code == 200:
                records_data = response.json()
                content = records_data.get("content", [])
                total_elements = records_data.get("totalElements", 0)
                total_pages = records_data.get("totalPages", 0)

                if not content:
                    await show_records.send("暂无历史记录。")
                    return

                message = "历史记录：\n"
                for record in content:
                    record_time = record.get("playTime", "")
                    arcade_name = record.get("arcadeName", "未知机厅")
                    song_name = record.get("songName", "未知歌曲")
                    score = record.get("score", 0)
                    difficulty = record.get("difficulty", "未知")

                    try:
                        if record_time:
                            record_time = datetime.strptime(record_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%m/%d %H:%M")
                    except ValueError:
                        pass

                    message += f"{record_time} | {song_name} | {difficulty} | {score}\n"

                message += f"\n共 {total_elements} 条记录，当前 {page}/{total_pages} 页"
                if total_pages > 1:
                    message += "\n可以在命令后添加页数查看对应页数的记录。"

                await show_records.send(message)
            elif response.status_code == 400:
                await show_records.send("请求数据不合法，请检查请求。")
            elif response.status_code == 401:
                await show_records.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_records.send("权限不足，无法获取历史记录。")
            elif response.status_code == 410:
                await show_records.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_records.send(f"{error_message}")
            else:
                await show_records.send(f"获取历史记录失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await show_records.send(f"获取历史记录过程中出现错误：{e}")


@show_user_settings.handle()
async def handle_show_user_settings(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_user_settings()
    @Description: 处理用户查看设置操作
    @Param {MessageEvent} event: 消息事件
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/showSettings 查看设置】
用法：/showSettings
别名：/settings, /查看设置, /显示设置, /用户设置

功能：查看您当前的用户设置。

API接口：GET /web/showUserSettings
无需请求参数

可设置项包括：
  - allowSearch (允许好友查找)
  - showOnlineStatus (显示在线状态)
  - showPlayHistory (显示游玩历史)
  - allowFriendRequest (允许好友请求)
  - showRating (显示 Rating)
  - showAchievement (显示成就)"""
        await show_user_settings.send(help_text)
        return
    
    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await show_user_settings.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/web/showUserSettings', headers=headers)

            if response.status_code == 200:
                settings_data = response.json()
                message = "用户设置：\n"
                for key, value in settings_data.items():
                    setting_name = get_setting_name(key)
                    setting_value = "开启" if value is True else "关闭" if value is False else str(value)
                    message += f"{setting_name}：{setting_value}\n"
                await show_user_settings.send(message)
            elif response.status_code == 401:
                await show_user_settings.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_user_settings.send("权限不足，无法获取用户设置。")
            elif response.status_code == 410:
                await show_user_settings.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_user_settings.send(f"{error_message}")
            else:
                await show_user_settings.send(f"获取用户设置失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await show_user_settings.send(f"获取用户设置过程中出现错误：{e}")


@set_user_settings.handle()
async def handle_set_user_settings(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_set_user_settings()
    @Description: 处理用户修改设置操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 设置参数 (格式: 设置名 值)
    """
    args = str(arg).strip()
    
    # help 功能
    if args.lower() == 'help':
        help_text = """【/setSettings 修改设置】
用法：/setSettings <设置名> <值>
别名：/设置, /修改设置

参数说明：
  设置名 - 要修改的设置项（必填）
  值 - 新的设置值（必填，支持: true/false/开启/关闭）

可修改的设置项：
  - allowSearch (允许好友查找)
  - showOnlineStatus (显示在线状态)
  - showPlayHistory (显示游玩历史)
  - allowFriendRequest (允许好友请求)
  - showRating (显示 Rating)
  - showAchievement (显示成就)

API接口：POST /web/setUserSettings
请求体：{"policyName": "string", "policy": "EVERYONE"}

示例：/setSettings showRating 开启"""
        await set_user_settings.send(help_text)
        return
    
    args_list = args.split()
    qqid = str(event.get_user_id())

    if len(args_list) < 2:
        await set_user_settings.send("请提供设置名和值，格式：/setSettings 设置名 值")
        return

    setting_key = args_list[0]
    setting_value = args_list[1]

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await set_user_settings.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    # 尝试将值转换为布尔类型
    if setting_value.lower() in ['true', '开启', '是', 'on', '1']:
        setting_value = True
    elif setting_value.lower() in ['false', '关闭', '否', 'off', '0']:
        setting_value = False

    payload = {setting_key: setting_value}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/web/setUserSettings', json=payload, headers=headers)

            if response.status_code == 200:
                await set_user_settings.send("设置修改成功！")
            elif response.status_code == 400:
                await set_user_settings.send("请求数据不合法，请检查设置名和值。")
            elif response.status_code == 401:
                await set_user_settings.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await set_user_settings.send("权限不足，无法修改设置。")
            elif response.status_code == 410:
                await set_user_settings.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await set_user_settings.send(f"{error_message}")
            else:
                await set_user_settings.send(f"修改设置失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await set_user_settings.send(f"修改设置过程中出现错误：{e}")


@set_avatar.handle()
async def handle_set_avatar_start(event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_set_avatar_start()
    @Description: 处理用户设置头像操作 - 第一步，检查绑定并提示上传图片
    @Param {MessageEvent} event: 消息事件
    @Param {T_State} state: 会话状态
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/setAvatar 设置头像】
用法：/setAvatar
别名：/setavatar, /设置头像, /修改头像

功能：设置您的头像。
使用方法：输入命令后，根据提示发送图片即可。

API接口：POST /web/setAvatar
请求体：{"avatarBase64": "string"}

注意：图片将被base64编码后上传，超时时间为60秒。"""
        await set_avatar.finish(help_text)
    
    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await set_avatar.finish("您尚未绑定，请先绑定。")

    state["bot_key"] = bot_key


@set_avatar.got("avatar_image", prompt="请发送您要上传的图片（超时时间60秒）")
async def handle_set_avatar_receive(event: MessageEvent, state: T_State):
    """
    @Author: TurboServlet
    @Func: handle_set_avatar_receive()
    @Description: 处理用户设置头像操作 - 第二步，接收图片并上传
    @Param {MessageEvent} event: 消息事件
    @Param {T_State} state: 会话状态
    """
    bot_key = state.get("bot_key")
    message = event.get_message()

    # 提取图片
    image_url = None
    for seg in message:
        if seg.type == "image":
            image_url = seg.data.get("url")
            break

    if not image_url:
        await set_avatar.reject("未检测到图片，请发送一张图片。")

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        # 下载图片
        async with httpx.AsyncClient(timeout=30.0) as client:
            img_response = await client.get(image_url)
            if img_response.status_code != 200:
                await set_avatar.finish("图片下载失败，请重试。")

            image_data = img_response.content
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 上传头像
            payload = {"avatarBase64": image_base64}
            response = await client.post(
                f'{Config.api_base_url}/web/setAvatar',
                json=payload,
                headers=headers,
                timeout=60.0
            )

            if response.status_code == 200:
                await set_avatar.finish("头像设置成功！")
            elif response.status_code == 400:
                await set_avatar.finish("请求数据不合法，请检查图片格式。")
            elif response.status_code == 401:
                await set_avatar.finish("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await set_avatar.finish("权限不足，无法设置头像。")
            elif response.status_code == 410:
                await set_avatar.finish("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await set_avatar.finish(f"{error_message}")
            else:
                await set_avatar.finish(f"设置头像失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await set_avatar.finish(f"设置头像过程中出现错误：{e}")


@reset_avatar.handle()
async def handle_reset_avatar(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_reset_avatar()
    @Description: 处理用户重置头像操作
    @Param {MessageEvent} event: 消息事件
    """
    # help 功能
    if str(arg).strip().lower() == 'help':
        help_text = """【/resetAvatar 重置头像】
用法：/resetAvatar
别名：/resetavatar, /重置头像, /删除头像

功能：将您的头像重置为默认状态。

API接口：POST /web/resetAvatar
无需请求体参数"""
        await reset_avatar.send(help_text)
        return
    
    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await reset_avatar.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/web/resetAvatar', headers=headers)

            if response.status_code == 200:
                await reset_avatar.send("头像重置成功！")
            elif response.status_code == 400:
                await reset_avatar.send("重置头像失败，请求数据不合法。")
            elif response.status_code == 401:
                await reset_avatar.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await reset_avatar.send("权限不足，无法重置头像。")
            elif response.status_code == 410:
                await reset_avatar.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await reset_avatar.send(f"{error_message}")
            else:
                await reset_avatar.send(f"重置头像失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await reset_avatar.send(f"重置头像过程中出现错误：{e}")


@set_friend_search_policy.handle()
async def handle_set_friend_search_policy(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_set_friend_search_policy()
    @Description: 处理用户设置好友查找策略操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 策略值 (开启/关闭 或 true/false)
    """
    policy_str = str(arg).strip().lower()
    
    # help 功能
    if policy_str == 'help':
        help_text = """【/setSearchPolicy 设置好友查找】
用法：/setSearchPolicy <策略>
别名：/setsearchpolicy, /设置好友查找, /好友查找设置

参数说明：
  策略 - 开启/关闭 或 true/false（必填）

功能：设置是否允许其他用户通过查找找到您。

API接口：POST /web/setFriendSearchPolicy
请求体：{"policy": "AUTO_ACCEPT"}

示例：/setSearchPolicy 开启"""
        await set_friend_search_policy.send(help_text)
        return

    qqid = str(event.get_user_id())

    if not policy_str:
        await set_friend_search_policy.send("请提供好友查找策略：开启 或 关闭")
        return

    if policy_str in ['true', '开启', '是', 'on', '1', '允许']:
        policy = True
    elif policy_str in ['false', '关闭', '否', 'off', '0', '禁止']:
        policy = False
    else:
        await set_friend_search_policy.send("无效的策略值，请使用：开启 或 关闭")
        return

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await set_friend_search_policy.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"allowSearch": policy}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/web/setFriendSearchPolicy', json=payload, headers=headers)

            if response.status_code == 200:
                status = "开启" if policy else "关闭"
                await set_friend_search_policy.send(f"好友查找策略已设置为：{status}")
            elif response.status_code == 400:
                await set_friend_search_policy.send("请求数据不合法，请检查输入。")
            elif response.status_code == 401:
                await set_friend_search_policy.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await set_friend_search_policy.send("权限不足，无法设置好友查找策略。")
            elif response.status_code == 410:
                await set_friend_search_policy.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await set_friend_search_policy.send(f"{error_message}")
            else:
                await set_friend_search_policy.send(f"设置失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await set_friend_search_policy.send(f"设置好友查找策略过程中出现错误：{e}")


@show_rivals.handle()
async def handle_show_rivals(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_rivals()
    @Description: 处理用户获取对手列表操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 页码（可选）
    """
    page_str = str(arg).strip()
    
    # help 功能
    if page_str.lower() == 'help':
        help_text = """【/showRivals 对手列表】
用法：/showRivals [页码]
别名：/showrivals, /rivals, /对手, /对手列表, /查询对手, /查看对手

参数说明：
  页码 - 可选，默认为1（Int类型）

功能：查看您的对手列表，支持分页显示。

API接口：GET /web/showRivals
查询参数：page (Int)

示例：/showRivals 2"""
        await show_rivals.send(help_text)
        return
    
    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if page_str.isdigit():
        page = int(page_str)
    else:
        page = 1

    if not bot_key:
        await show_rivals.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{Config.api_base_url}/web/showRivals', params={"page": page}, headers=headers)

            if response.status_code == 200:
                rivals_data = response.json()
                content = rivals_data.get("content", [])
                total_elements = rivals_data.get("totalElements", 0)
                total_pages = rivals_data.get("totalPages", 0)

                if not content:
                    await show_rivals.send("您目前还没有添加对手。")
                    return

                rival_names = [rival.get("turboName", "未知") for rival in content]
                rival_list_message = "对手列表：\n" + "\n".join(rival_names)

                message = (
                    f"{rival_list_message}\n\n"
                    f"共 {total_elements} 位对手，当前 {page}/{total_pages} 页。"
                )

                if total_pages > 1:
                    message += "\n可以在命令后添加页数查看对应页数的对手。"

                await show_rivals.send(message)
            elif response.status_code == 400:
                await show_rivals.send("请求数据不合法，请检查请求。")
            elif response.status_code == 401:
                await show_rivals.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_rivals.send("权限不足，无法获取对手列表。")
            elif response.status_code == 410:
                await show_rivals.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_rivals.send(f"{error_message}")
            else:
                await show_rivals.send(f"获取对手列表失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await show_rivals.send(f"获取对手列表过程中出现错误：{e}")


@add_rival.handle()
async def handle_add_rival(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_add_rival()
    @Description: 处理用户添加对手操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 对手名称
    """
    turbo_name = str(arg).strip()
    
    # help 功能
    if turbo_name.lower() == 'help':
        help_text = """【/addRival 添加对手】
用法：/addRival <turboName>
别名：/addrival, /添加对手, /加对手

参数说明：
  turboName - 要添加的对手名称（必填，string类型）

功能：添加指定用户为您的对手。

API接口：POST /web/addRival
请求体：{"turboName": "string"}

示例：/addRival 张三"""
        await add_rival.send(help_text)
        return
    
    qqid = str(event.get_user_id())

    if not turbo_name:
        await add_rival.send("请提供要添加的对手名称。")
        return

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await add_rival.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"turboName": turbo_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/web/addRival', json=payload, headers=headers)

            if response.status_code == 200:
                await add_rival.send(f"已成功添加对手：{turbo_name}")
            elif response.status_code == 400:
                await add_rival.send("请求数据不合法，请检查输入的对手名称。")
            elif response.status_code == 401:
                await add_rival.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await add_rival.send("权限不足，无法添加对手。")
            elif response.status_code == 410:
                await add_rival.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await add_rival.send(f"{error_message}")
            else:
                await add_rival.send(f"添加对手失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await add_rival.send(f"添加对手过程中出现错误：{e}")


@remove_rival.handle()
async def handle_remove_rival(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_remove_rival()
    @Description: 处理用户删除对手操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 对手名称
    """
    turbo_name = str(arg).strip()
    
    # help 功能
    if turbo_name.lower() == 'help':
        help_text = """【/removeRival 删除对手】
用法：/removeRival <turboName>
别名：/removerival, /删除对手, /移除对手

参数说明：
  turboName - 要删除的对手名称（必填，string类型）

功能：从对手列表中删除指定用户。

API接口：POST /web/removeRival
请求体：{"turboName": "string"}

示例：/removeRival 李四"""
        await remove_rival.send(help_text)
        return
    
    qqid = str(event.get_user_id())

    if not turbo_name:
        await remove_rival.send("请提供要删除的对手名称。")
        return

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await remove_rival.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"turboName": turbo_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{Config.api_base_url}/web/removeRival', json=payload, headers=headers)

            if response.status_code == 200:
                await remove_rival.send(f"已成功删除对手：{turbo_name}")
            elif response.status_code == 400:
                await remove_rival.send("请求数据不合法，请检查输入的对手名称。")
            elif response.status_code == 401:
                await remove_rival.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await remove_rival.send("权限不足，无法删除对手。")
            elif response.status_code == 410:
                await remove_rival.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await remove_rival.send(f"{error_message}")
            else:
                await remove_rival.send(f"删除对手失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await remove_rival.send(f"删除对手过程中出现错误：{e}")


def get_setting_name(key: str) -> str:
    """
    @Author: TurboServlet
    @Func: get_setting_name()
    @Description: 获取设置名称的中文描述
    @Param {str} key: 设置键名
    @Return: str
    """
    setting_names = {
        'allowSearch': '允许好友查找',
        'showOnlineStatus': '显示在线状态',
        'showPlayHistory': '显示游玩历史',
        'allowFriendRequest': '允许好友请求',
        'showRating': '显示 Rating',
        'showAchievement': '显示成就',
    }
    return setting_names.get(key, key)
