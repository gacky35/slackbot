from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackbot.bot import default_reply
from . import subMethod

@listen_to('@[a-zA-Z0-9]+\s([\s\S]*)')
def reply_to_thread(message, text):
    usergroup = subMethod.get_usergroup_list()
    message.body['text'].replace('\n', ' ')
    mention = message.body['text'].split()[0].strip('@')
    mention_dict = []
    for dictionary in usergroup:
        if dictionary['usergroup_name'] == mention:
            mention_dict = dictionary
            break
    if len(mention_dict) == 0:
        message.send('`' + mention + ' is not exist`')
        return
    sentence = ""
    for member in mention_dict['member']:
        sentence = sentence + "<@" + member + "> "
    sentence = sentence + "\n"
    message.send(sentence, 
            thread_ts=message.thread_ts)

@respond_to('count')
def count_up_reaction(message):
    response = subMethod.get_message(message.body['channel'], 
                                    message.thread_ts)
    if not response:
        message.direct_reply("Can't use count method in DM")
        return
    sentence = ''
    if 'reactions' in response['messages'][0]:
        data = response['messages'][0]['reactions']
        sorted_data = sorted(data, reverse=True, key=lambda x:x['count'])
        sentence = response['messages'][0]['text'] + '\n\n*Result*\n'
        for datum in sorted_data:
            sentence = sentence + ":" + datum['name'] + ":" + " "
            for user in datum['users']:
                sentence = sentence + "<@" + user + "> "
            sentence = sentence + "\n"
    else:
        sentence = 'No reactions'
    message.direct_reply(sentence)

@respond_to('diff')
def check_reactor(message):
    response = subMethod.get_message(message.body['channel'],
                                    message.thread_ts)
    if not response:
        message.direct_reply("Can't use count method in DM")
        return
    target_usergroup = response['messages'][0]['text'].replace('\n', ' ').split()[0].strip('@')
    all_target_audience = subMethod.get_usergroup_member_id(target_usergroup)
    if len(all_target_audience) == 0:
        sentence = 'No specified user group'
    elif 'reactions' in response['messages'][0]:
        data = response['messages'][0]['reactions']
        reacted_users = []
        reacted_users.extend([user for datum in data for user in datum['users']])
        target_audience = []
        target_audience.extend([user for user in all_target_audience if user not in reacted_users])
        sentence = "*Hasn't yet reacted*\n"
        for user in target_audience:
            sentence = sentence + "<@" + user + ">\n"
    else:
        sentence = "*Hasn't yet reacted*\n"
        for user in all_target_audience:
            sentence = sentence + "<@" + user + ">\n"
    message.direct_reply(sentence)


@respond_to('create\s([a-zA-Z0-9]*)\s([\w\s,]+)')
def create_usergroup(message, usergroup_name, member):
    usergroup = subMethod.get_usergroup_list()
    member_list = subMethod.get_member()['members']
    for usergroup_dict in usergroup:
        if usergroup_dict['usergroup_name'] == usergroup_name:
            message.send("`" + usergroup_name+' is already exist.`\n> please choose another name.')
            return
    data = {}
    member_id = []
    data['usergroup_name'] = usergroup_name
    try:
        member_name = [x.strip() for x in member.split(',')]
    except AttributeError:
        member_name = []
        member_id = member
    ml_id = [ml['id'] for ml in member_list]
    ml_name = [ml['name'] for ml in member_list]
    ml_rname = [ml['real_name'] if 'real_name' in ml else 'no_name' for ml in member_list]
    ml_dname = [ml['profile']['display_name'] for ml in member_list]
    for mn in member_name:
        if mn in ml_name:
            member_id.append(ml_id[ml_name.index(mn)])
        elif mn in ml_rname:
            member_id.append(ml_id[ml_rname.index(mn)])
        elif mn in ml_dname:
            member_id.append(ml_id[ml_dname.index(mn)])
        else:
            message.send("`" + mn + " is not in this channel`")
    data['member'] = member_id
    usergroup.append(data)
    subMethod.set_usergroup_list(usergroup)
    message.send('Created a usergroup')

@respond_to('merge\s([a-zA-Z0-9]*)\s([a-zA-Z0-9,]*)')
def merge_usergroup(message, usergroup_name, member):
    usergroups = subMethod.get_usergroup_list()
    merge_group_list = member.split(',')
    merge_list = []
    [merge_list.extend(usergroup['member']) for usergroup in usergroups if usergroup['usergroup_name'] in merge_group_list]
    usergroups_name = [usergroup['usergroup_name'] for usergroup in usergroups]
    if usergroup_name in usergroups_name:
        add_member(message, usergroup_name, merge_list)
    else:
        create_usergroup(message, usergroup_name, merge_list)
    
@respond_to('prune\s([a-zA-Z0-9]*)\s([a-zA-Z0-9,]*)')
def prune_usergroup(message, usergroup_name, member):
    usergroups = subMethod.get_usergroup_list()
    prune_group_list = member.split(',')
    prune_list = []
    [prune_list.extend(usergroup['member']) for usergroup in usergroups if usergroup['usergroup_name'] in prune_group_list]
    delete_member(message, usergroup_name, prune_list)

@respond_to('add\s([a-zA-Z0-9]*)\s([\w\s,]+)')
def add_member(message, usergroup_name, member):
    usergroup = subMethod.get_usergroup_list()
    usergroup_name_list = [usergroup_dict['usergroup_name'] for usergroup_dict in usergroup]
    if usergroup_name not in usergroup_name_list:
        message.send("`" + usergroup_name + " is not exist`\n> please type `@secretary list` and check usergroup_name.")
        return
    member_list = subMethod.get_member()['members']
    usergroup_member = subMethod.get_usergroup_member(usergroup_name)

    member_id = []
    try:
        member_name = [x.strip() for x in member.split(',')]
    except AttributeError:
        member_name = []
        member_id = member
    add_member_name = []
    for mn in member_name:
        if mn not in usergroup_member:
            add_member_name.append(mn)
        else:
            message.send("`" + mn + ' already belongs`')
    ml_id = [ml['id'] for ml in member_list]
    ml_name = [ml['name'] for ml in member_list]
    ml_rname = [ml['real_name'] if 'real_name' in ml else 'no_name' for ml in member_list]
    ml_dname = [ml['profile']['display_name'] for ml in member_list]
    for mn in add_member_name:
        if mn in ml_name:
            member_id.append(ml_id[ml_name.index(mn)])
        elif mn in ml_rname:
            member_id.append(ml_id[ml_rname.index(mn)])
        elif mn in ml_dname:
            member_id.append(ml_id[ml_dname.index(mn)])
        else:
            message.send("`" + mn + " is not in this channel`")
    if len(member_id) == 0:
        message.send("`No one will add`")
        return
    for usergroup_dict in usergroup:
        if usergroup_dict['usergroup_name'] == usergroup_name:
            usergroup_dict['member'].extend(member_id)
            usergroup_dict['member'] = list(set(usergroup_dict['member']))
            break
    subMethod.set_usergroup_list(usergroup)
    message.send('Added some member')

@respond_to('delete\s([a-zA-Z0-9]*)\s([\w\s,]+)')
def delete_member(message, usergroup_name, member):
    usergroup = subMethod.get_usergroup_list()
    usergroup_name_list = [usergroup_dict['usergroup_name'] for usergroup_dict in usergroup]
    if usergroup_name not in usergroup_name_list:
        message.send("`" + usergroup_name + " is not exist`\n> type `@secretary list` and check usergroup_name")
        return
    member_list = subMethod.get_member()['members']
    member_id = []
    try:
        member_name = [x.strip() for x in member.split(',')]
    except AttributeError:
        member_name = []
        member_id = member
    ml_id = [ml['id'] for ml in member_list]
    ml_name = [ml['name'] for ml in member_list]
    ml_rname = [ml['real_name'] if 'real_name' in ml else 'no_name' for ml in member_list]
    ml_dname = [ml['profile']['display_name'] for ml in member_list]
    for mn in member_name:
        if mn in ml_name:
            member_id.append(ml_id[ml_name.index(mn)])
        elif mn in ml_rname:
            member_id.append(ml_id[ml_rname.index(mn)])
        elif mn in ml_dname:
            member_id.append(ml_id[ml_dname.index(mn)])
        else:
            message.send("`" + mn + " is not in this channel`")
    if len(member_id) == 0:
        message.send("`No one will delete`")
        return
    for usergroup_dict in usergroup:
        if usergroup_dict['usergroup_name'] == usergroup_name:
            for mi in member_id:
                if mi not in usergroup_dict['member']:
                    message.send("`" + ml_name[ml_id.index(mi)] + " doesn't belong to this`")
                else:
                    usergroup_dict['member'].remove(mi)
            break
    subMethod.set_usergroup_list(usergroup)
    message.send('Deleted some member')

@respond_to('delete_usergroup\s([a-zA-Z0-9]*)')
def delete_usergroup(message, usergroup_name):
    usergroup = subMethod.get_usergroup_list()
    usergroup_name_list = [x['usergroup_name'] for x in usergroup]
    if usergroup_name not in usergroup_name_list:
        message.send("`" + usergroup_name + ' is not exist.`\n> type `@secretary list` and check usergroup_name')
        return
    new_usergroup = []
    for usergroup_dict in usergroup:
        if usergroup_dict['usergroup_name'] == usergroup_name:
            continue
        new_usergroup.append(usergroup_dict)
    subMethod.set_usergroup_list(new_usergroup)
    message.send('Deleted a usergroup')

@respond_to('rename\s([a-zA-Z0-9]*)\s([a-zA-Z0-9]*)')
def rename_usergroup(message, usergroup_name, new_usergroup_name):
    usergroups = subMethod.get_usergroup_list()
    usergroup_name_list = [x['usergroup_name'] for x in usergroups]
    if usergroup_name not in usergroup_name_list:
        message.send("`" + usergroup_name + ' is not exist.`')
        return
    if new_usergroup_name in usergroup_name_list:
        message.send("`" + new_usergroup_name + ' is exist.`\n> please choose another name')
        return
    for usergroup in usergroups:
        if usergroup['usergroup_name'] == usergroup_name:
            usergroup['usergroup_name'] = new_usergroup_name
            break
    subMethod.set_usergroup_list(usergroups)
    message.send('Renamed a usergroup')

@respond_to('list')
def show_usergroup_list(message):
    usergroup = subMethod.get_usergroup_list()
    sentence = "*List of Resisted Usergroup*\n>>>"
    for usergroup_dict in usergroup:
        sentence = sentence + usergroup_dict['usergroup_name'] + "\n"
    message.send(sentence)

@respond_to('show\s([a-zA-Z0-9]*)')
def show_usergroup_member(message, usergroup_name):
    usergroup = subMethod.get_usergroup_list()
    user_list = subMethod.get_member()['members']
    sentence = "`" + usergroup_name + " has not created.`\n> please type `@secretary list` and check usergroup_name."
    for usergroup_dict in usergroup:
        if usergroup_dict['usergroup_name'] == usergroup_name:
            members = subMethod.userid_to_username(user_list, usergroup_dict['member'])
            sentence = "Member of *" + usergroup_name + "*\n>>>"
            for member in members:
                sentence = sentence + member + "\n"
            break
    message.send(sentence)

@respond_to('absent\s([\s\S]+)')
def absent(message, reason):
    template = reason.split()
    if len(template) < 3:
        message.direct_reply('few argument')
        return
    subMethod.send_message('absent', template[0] + ' ' + template[1] + 'です.\n' + template[2] + 'のため本日の活動を欠席します.\n')
   

@respond_to('help')
def show_help_message(message):
    message.send('You can use these commands.\n'\
                'You have to mention to *@secretary* for use these commands.\n'\
                '>>> `create [usergroup_name] [member,member,...]` : create new usergroup.\n'\
                '`add [usergroup_name] [member,member,...]` : add member to exist usergroup.\n'\
                '`delete [usergroup_name] [member,member,...]` : remove member from usergroup.\n'\
                '`delete_usergroup [usergroup_name]` : delete a specified usergroup.\n'\
                '`rename [usergroup_name] [new_usergroup_name]` : change usergroup_name.\n'\
                '`list` : show all usergroup.\n'\
                '`show [usergroup_name]` : show members belonging to a specified usergroup.\n'\
                '`count` : send questionnare\'s result to your DM. this command can only be used on threads. \n')
    
