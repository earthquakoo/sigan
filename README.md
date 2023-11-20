<h1 align="center">🙏 Sigan - Very simple CLI slack alarm manager 🙏</h1>

<h4 align="center">A convenient app that allows you to set alarms through a simple CLI. Create alarms in Slack with simple commands!</h4>

# 🛑 Archive

This project has been archived to better serve you.
I'll come back with a better service.

# 🛎 Current Version `0.1.21`

#### Upgrade with `pip install sigan --upgrade`

# 🚀 Installation & Settings


First, you need to download the Slack app by clicking the link below.
(You can choose the workspace where you want to install it in the upper right corner of the link.)

<h5 align="center"><a href="https://siganserver.com/slack/install"><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcSet="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a></h5>

Although it has not been officially approved by Slack yet, it will be approved in the future. Rest assured, it is not a hacking program!


Once you have downloaded the "Sigan Slack App" through the link, you will receive a message as shown below. Check if the team ID has arrived in the message and copy it!
![[register message.png]]

Next, make sure that Python is version `3.9` or higher. Then enter the following commands in the terminal:

```bash
pip install sigan
```

After the installation is complete, proceed with registration using the following command:

```bash
sigan register
```

You will be prompted to enter the team ID that you copied earlier
![[register1.png]]

If you entered the correct team ID, you will receive a message confirming that the registration is complete.

Now, you are all set! However, please check a few restrictions.

# ⚠️ Restrictions

- You can set message reservations up to 120 days in the future.

- You cannot schedule more than 30 messages within 5 minutes in the same channel.
	-  [Slack API reference](https://api.slack.com/methods/chat.scheduleMessage#restrictions)

- If a scheduled message is going to be sent within 5 minutes, it cannot be deleted, resulting in an error.
- This may be a bug, as the official documentation states within 1 minute, but the API returns "OK" while it fails in the background.
	- [Slack API reference](https://api.slack.com/methods/chat.deleteScheduledMessage#restrictions)
	- [Reference](https://stackoverflow.com/questions/67575370/deleted-scheduled-messages-still-sending)

- Sigan bot operates in a single Slack workspace only.
	- If you want to use it in a different Slack workspace, you need to install it in the new workspace through the "App to Slack" link at the top and run sigan register again.
	- You also need to remove the existing Sigan bot from the previous Slack workspace.

# 👨‍💻 Commands

## 0. Information

If you want to know the general information about commands, you can use the following command:

```bash
sigan --help
```

![[sigan help.png]]

For more detailed information about specific commands, you can use the following command:

```bash
sigan <command name> --help 
```

You can check the version of the Sigan CLI with the following command:

```bash
sigan --version
```
## 1. add command

```bash
sigan add <content> [-d | --deadline <deadline date>] [-t | --time <notification date> [-i | --interval <day of the week>] [-b | --before <Set confirm alarm date x days before deadline>]] [-c | --channel <Select slack channel>]
```

### 1.1 add command rule < content >

- `<content>` is **required**.
- If there are spaces in the content, please use `""` to enter it. If there are no spaces, you can omit `""`.
### 1.2 add command rule < deadline >

-  `-d | --deadline <deadline date>`  is **optional**.
- When setting a deadline, a confirmation alarm will be sent one day before the deadline, separate from the notification time.
	- If you want to set a different number of days before the deadline instead of one day, you can use the `-b | --before` command to specify how many days before the deadline.
	- If you don't set a deadline, a confirmation alarm will not be sent.

### 1.3 add command rule < notification time > 

- `-t | --time <notification date>` is somewhat **optional**.
- If you enter a date without specifying a time, the default time of 09:00 will be set.
- If you only enter a time, you must use the `-i | --interval` command to set the repeat interval.
	- ex) `sigan add "notification setting" -t 12:10 -i thu`

### 1.4 add command rule < interval >

-  `-i | --interval <day of the week>` is somewhat **optional**.
-If you want to send alarms on more than two days of the week, you can use ``""`` to select multiple days.
	- ex) `sigan add "interval setting" -t 15:00 -i "mon fri"`
- If you have both date and time specified for the alarm, you cannot use the interval command.

### 1.5 add command rule < before >

-  `-b | --before <Set confirm alarm date x days before deadline>` is **optional**.
	- ex) `sigan add "before test" -d 10/20 -t 14:00 -i mon -b 3`

### 1.6 add command rule < channel >

-  `-c | --channel <Select slack channel>` is **optional**.
- To select a channel, you must first invite the Sigan bot to that channel.
	- Enter the name of the channel where the Sigan bot was invited and the alarm will be sent to that channel.
- If you do not select a channel, the alarm will be sent to Sigan bot's DM.

## 2. show command

You can use the `show` command to check alarm events.

```bash
sigan show
```

![[sigan show.png]]
## 3. delete command

You can delete existing alarms using the `delete` command.

```bash
sigan delete <alarm_id> [-y | --yes]
```

You can use `-y | --yes` to suppress the confirmation prompt when deleting alarms. If you don't use it, a confirmation prompt will be shown when deleting alarms.
## 4. chcnt command

You can change the content of existing alarms using the `chcnt `command.

```bash
sigan chcnt <alarm_id> <content>
```

ex) `sigan chcnt 1 "test content change"`
## 5. chdl command

You can change the deadline of existing alarms using the `chdl` command.

```bash
sigan chdl <alarm_id> <deadline>
```

ex) `sigan chdl 1 12/25`, `sigan chdl 1 "2023/12/25"`

You cannot set a deadline that is earlier than the notification time of the existing alarm.
## 6. chdate command

You can change the notification time of existing alarms using the `chdate` command.

```bash
sigan chdate <alarm_id> <date>
```

- To change only the time
	- ex) `sigan chdate 1 -d 15:00`
- To change only the date
	- ex) `sigan chdate 1 10/24`, `sigan chdate 1 "2023/10/24"`
- To change both the date and time
	- ex) `sigan chdate 1 "2023/12/10 15:00"`

## 7. chinv command

You can change the interval of existing alarms using the `chinv` command.

```bash
sigan chinv <alarm_id> <interval>
```

ex) `sigan chinv 1 wed`

# ⏭ What's next?

1. Interworking with Google Calendar
2. Add slack slash command


# 🚮 Uninstalling

If, for some reason, you want to uninstall the app, you can do so with the following command:

```bash
pip uninstall sigan
```