import asyncio
import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import os
import time
from datetime import datetime

# ========== НАСТРОЙКИ ==========
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Токен не найден! Установите переменную DISCORD_TOKEN")
    exit()

# ТВОИ НАСТРОЙКИ
GUILD_ID = 862025227491213362
CHANNEL_APPLICATIONS = 1232678532501475338
CHANNEL_MODERATION = 1455277143037841726
CHANNEL_DECISIONS = 1455628223890063511

ROLE_LEADER = 898200620484419634
ROLE_DEPUTY = 1232399561486766130
ROLE_HOMIE = 1232443801222778911

# Хранилище
applications = {}
moderation_messages = {}

# ========== БОТ ==========
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ========== НАСТРОЙКИ ==========
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Токен не найден! Установите переменную DISCORD_TOKEN")
    exit()

# ТВОИ НАСТРОЙКИ
GUILD_ID = 862025227491213362
CHANNEL_APPLICATIONS = 1232678532501475338
CHANNEL_MODERATION = 1455277143037841726
CHANNEL_DECISIONS = 1455628223890063511

ROLE_LEADER = 898200620484419634
ROLE_DEPUTY = 1232399561486766130
ROLE_HOMIE = 1232443801222778911

# Хранилище
applications = {}
moderation_messages = {}

# ========== БОТ ==========
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ========== ФОРМА ЗАЯВКИ (5 ВОПРОСОВ) ==========
class ApplicationForm(Modal):
    def __init__(self):
        super().__init__(title="📝 Заявка в семью BESPREDEL")

        # 1. Имя и возраст
        self.name_age = TextInput(
            label="1. Имя и возраст",
            placeholder="Дмитрий, 22 года",
            required=True,
            max_length=100
        )
        self.add_item(self.name_age)

        # 2. Статические ID всех персонажей
        self.char_ids = TextInput(
            label="2. ID всех персонажей",
            placeholder="1, 2, 3, 4...",
            required=True,
            max_length=200
        )
        self.add_item(self.char_ids)

        # 3. Онлайн и цель (теперь ТОЛЬКО онлайн)
        self.online = TextInput(
            label="3. Суточный онлайн",
            placeholder="8-10 часов",
            required=True,
            max_length=100
        )
        self.add_item(self.online)

        # 4. Цель вступления (отдельное поле)
        self.goal = TextInput(
            label="4. Цель вступления",
            placeholder="Почему хотите вступить в семью?",
            required=True,
            max_length=500
        )
        self.add_item(self.goal)

        # 5. Откат стрельбы
        self.shooting = TextInput(
            label="5. Откат стрельбы (YouTube)",
            placeholder="https://youtube.com/watch?v=...",
            required=True,
            max_length=200
        )
        self.add_item(self.shooting)

    async def on_submit(self, interaction: discord.Interaction):
        app_id = f"{interaction.user.id}_{int(time.time())}"
        applications[app_id] = {
            "user": interaction.user,
            "user_id": interaction.user.id,
            "answers": [
                self.name_age.value,
                self.char_ids.value,
                self.online.value,
                self.goal.value,
                self.shooting.value
            ],
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }

        embed = discord.Embed(
            title="📨 Заявка отправлена",
            description="Ваша заявка успешно отправлена на рассмотрение!",
            color=0x2ecc71
        )

        embed.add_field(
            name="📋 Что дальше?",
            value=f"1. Заявка передана лидерам на проверку\n2. Решение будет в <#{CHANNEL_DECISIONS}>\n3. Ожидайте уведомления",
            inline=False
        )

        embed.set_footer(
            text=f"ID: {app_id[:8]} | Сообщение удалится через минуту",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
            delete_after=60
        )

        await send_to_moderation(app_id, interaction)

async def send_to_moderation(app_id, interaction):
    """Отправляет заявку в канал модерации"""
    app = applications.get(app_id)
    if not app:
        return

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    channel = guild.get_channel(CHANNEL_MODERATION)
    if not channel:
        print(f"⚠️ Канал модерации не найден! ID: {CHANNEL_MODERATION}")
        channel = guild.get_channel(CHANNEL_APPLICATIONS)
        if not channel:
            return

    answers = app["answers"]
    name_age = answers[0]
    char_ids = answers[1]
    online = answers[2]
    goal = answers[3]
    shooting = answers[4]

    embed = discord.Embed(
        title="",
        description="",
        color=0xffffff,
        timestamp=datetime.now()
    )

    embed.add_field(name="", value="**📋 НОВАЯ ЗАЯВКА**", inline=False)

    embed.add_field(
        name="",
        value=f"```fix\n👤 {name_age[:80]}```",
        inline=True
    )

    embed.add_field(
        name="",
        value=f"```fix\n🆔 {char_ids[:80]}```",
        inline=True
    )

    embed.add_field(name="\u200b", value="\u200b", inline=False)
    embed.add_field(name="**⏰ Суточный онлайн**", value=f"```\n{online[:100]}\n```", inline=False)
    embed.add_field(name="\u200b", value="\u200b", inline=False)
    embed.add_field(name="**🎯 Цель вступления в семью**", value=goal[:400], inline=False)
    embed.add_field(name="\u200b", value="\u200b", inline=False)
    embed.add_field(name="**🎥 Откат стрельбы**", value="", inline=False)

    if any(x in shooting.lower() for x in ["http", "youtube", "youtu.be"]):
        if "youtube.com/watch?v=" in shooting:
            video_id = shooting.split("v=")[1][:11]
            display_text = f"https://youtu.be/{video_id}"
        elif "youtu.be/" in shooting:
            display_text = shooting
        else:
            display_text = shooting[:50] + ("..." if len(shooting) > 50 else "")

        embed.add_field(name="", value=f"[{display_text}]({shooting})", inline=False)
    else:
        embed.add_field(name="", value=shooting[:200], inline=False)

    embed.add_field(name="\u200b", value="\u200b", inline=False)
    embed.add_field(name="\u200b", value="\u200b", inline=False)

    embed.add_field(
        name="**ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ**",
        value=(
            f"**ID заявки:** `{app_id[:8]}`\n"
            f"**Пользователь:** [{interaction.user.display_name}](https://discord.com/users/{interaction.user.id})\n"
            f"**User ID:** `{interaction.user.id}`\n"
            f"**Время подачи:** <t:{int(time.time())}:F>\n"
            f"**Прошло:** <t:{int(time.time())}:R>"
        ),
        inline=False
    )

    embed.set_footer(
        text="BESPREDEL Family • Используйте кнопки ниже",
        icon_url=interaction.guild.icon.url if interaction.guild.icon else None
    )

    if interaction.user.avatar:
        embed.set_thumbnail(url=interaction.user.avatar.url)

    view = ModerationView(app_id)
    content = f"<@&{ROLE_LEADER}> <@&{ROLE_DEPUTY}> 🔔 **Новая заявка!**"

    msg = await channel.send(content=content, embed=embed, view=view)
    moderation_messages[app_id] = msg.id
    print(f"✅ Заявка {app_id[:8]} отправлена в модерацию")

# ========== КНОПКИ МОДЕРАЦИИ ==========
class ModerationView(View):
    def __init__(self, app_id: str):
        super().__init__(timeout=None)
        self.app_id = app_id

    @discord.ui.button(label="✅ Принять", style=discord.ButtonStyle.success, emoji="✅", custom_id="approve_")
    async def approve_button(self, interaction: discord.Interaction, button: Button):
        if not await check_moderator(interaction.user):
            await interaction.response.send_message("❌ Только лидеры могут принимать заявки", ephemeral=True)
            return
        await process_decision(self.app_id, interaction, "approved", "Заявка принята")

    @discord.ui.button(label="❌ Отклонить", style=discord.ButtonStyle.danger, emoji="❌", custom_id="reject_")
    async def reject_button(self, interaction: discord.Interaction, button: Button):
        if not await check_moderator(interaction.user):
            await interaction.response.send_message("❌ Только лидеры могут отклонять заявки", ephemeral=True)
            return
        modal = RejectReasonModal(self.app_id)
        await interaction.response.send_modal(modal)

class RejectReasonModal(Modal):
    def __init__(self, app_id: str):
        super().__init__(title="Укажите причину отказа")
        self.app_id = app_id
        self.reason = TextInput(
            label="Причина отклонения",
            placeholder="Опишите причину...",
            required=True,
            max_length=1000
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await process_decision(self.app_id, interaction, "rejected", self.reason.value)

async def check_moderator(user: discord.Member) -> bool:
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return False

    member = guild.get_member(user.id)
    if not member:
        return False

    leader_role = guild.get_role(ROLE_LEADER)
    deputy_role = guild.get_role(ROLE_DEPUTY)

    has_leader = leader_role and leader_role in member.roles
    has_deputy = deputy_role and deputy_role in member.roles

    return has_leader or has_deputy

async def process_decision(app_id, interaction, decision, reason):
    if app_id not in applications:
        await interaction.response.send_message("❌ Заявка не найдена", ephemeral=True)
        return

    app = applications[app_id]
    app["status"] = decision
    app["moderator"] = str(interaction.user)
    app["reason"] = reason

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    if app_id in moderation_messages:
        try:
            channel = guild.get_channel(CHANNEL_MODERATION) or guild.get_channel(CHANNEL_APPLICATIONS)
            if channel:
                msg = await channel.fetch_message(moderation_messages[app_id])
                embed = msg.embeds[0]

                if decision == "approved":
                    embed.color = 0x2ecc71
                    embed.set_footer(text=f"✅ Принято | Модератор: {interaction.user}")
                else:
                    embed.color = 0xe74c3c
                    embed.set_footer(text=f"❌ Отклонено | Модератор: {interaction.user}")

                view = View()
                await msg.edit(embed=embed, view=view)
        except Exception as e:
            print(f"⚠️ Ошибка обновления: {e}")

    channel = guild.get_channel(CHANNEL_DECISIONS)
    if channel:
        if decision == "approved":
            title = "✅ ЗАЯВКА ПРИНЯТА"
            description = f"**{interaction.user.mention}** принял заявку!"
            color = 0x2ecc71

            try:
                member = guild.get_member(app['user_id'])
                homie_role = guild.get_role(ROLE_HOMIE)
                if member and homie_role:
                    await member.add_roles(homie_role)
                    description += f"\n\n🎉 **Роль <@&{ROLE_HOMIE}> выдана!**"
            except Exception as e:
                print(f"⚠️ Ошибка выдачи роли: {e}")
        else:
            title = "❌ ЗАЯВКА ОТКЛОНЕНА"
            description = f"**{interaction.user.mention}** отклонил заявку."
            color = 0xe74c3c

        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )

        embed.add_field(name="👤 Заявитель", value=f"<@{app['user_id']}>", inline=True)
        embed.add_field(name="👨‍⚖️ Модератор", value=interaction.user.mention, inline=True)

        if decision == "rejected":
            embed.add_field(name="📝 Причина", value=reason, inline=False)

        embed.set_footer(text="BESPREDEL Family • Система заявок")

        await channel.send(content=f"<@{app['user_id']}>", embed=embed)

    await interaction.response.send_message(f"✅ Заявка {decision}!", ephemeral=True)

# ========== КНОПКА ПОДАТЬ ЗАЯВКУ ==========
class ApplyButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Подать заявку", 
        style=discord.ButtonStyle.secondary, 
        custom_id="apply_button",
        emoji="📄",
        row=0
    )
    async def callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ApplicationForm())

# ========== СОБЫТИЯ БОТА ==========
@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен!")
    print(f"📊 Каналы: заявки={CHANNEL_APPLICATIONS}, модерация={CHANNEL_MODERATION}")
    print("=" * 50)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="заявки BESPREDEL"
        )
    )

    # Небольшая задержка для стабильности
    await asyncio.sleep(5)
    await setup_initial_message()

async def setup_initial_message():
    """Отправляет сообщение с кнопкой в канал заявок"""
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("❌ Сервер не найден")
        return

    channel = guild.get_channel(CHANNEL_APPLICATIONS)
    if not channel:
        print("❌ Канал заявок не найден")
        return

    try:
        async for msg in channel.history(limit=10):
            if msg.author == bot.user:
                await msg.delete()
    except:
        pass

    embed = discord.Embed(
        title="",
        description="",
        color=0x1a1a1a
    )

    embed.add_field(name="", value="\n**ЗАЯВКИ В СЕМЬЮ**\n", inline=False)

    embed.add_field(
        name="",
        value=(
            "**Путь в семью начинается здесь!**\n\n"
            "• Уведомление о приглашении на собеседование отправляется в личные сообщения. "
            "Если ЛС закрыты, оно отправляется в канал решений.\n\n"
            "• Обычно заявки обрабатываются в течение **3–7 дней** — всё зависит от того, "
            "насколько загружены наши рекрутеры на данный момент.\n\n"
            "• Подать заявку можно только при открытом наборе. "
            "Если кнопка не работает — набор закрыт."
        ),
        inline=False
    )

    embed.add_field(name="", value="\n**Для подачи заявки нажмите кнопку ниже:**", inline=False)

    embed.set_footer(
        text="BESPREDEL ERP | Система рекрутинга",
        icon_url=guild.icon.url if guild.icon else None
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await channel.send(embed=embed, view=ApplyButton())
    print("✅ Сообщение с кнопкой отправлено!")

# ========== КОМАНДЫ ==========
@bot.command()
async def обновить(ctx):
    """Обновить сообщение с кнопкой (админ)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Только для администраторов", delete_after=3)
        return

    await setup_initial_message()
    await ctx.send("✅ Сообщение обновлено!", delete_after=3)

@bot.command()
async def статус(ctx):
    """Показать статистику заявок"""
    pending = sum(1 for app in applications.values() if app["status"] == "pending")
    approved = sum(1 for app in applications.values() if app["status"] == "approved")
    rejected = sum(1 for app in applications.values() if app["status"] == "rejected")

    embed = discord.Embed(
        title="📊 СТАТИСТИКА BESPREDEL",
        color=0x9b59b6,
        timestamp=datetime.now()
    )

    embed.add_field(name="⏳ Ожидают", value=str(pending), inline=True)
    embed.add_field(name="✅ Принято", value=str(approved), inline=True)
    embed.add_field(name="❌ Отклонено", value=str(rejected), inline=True)
    embed.add_field(name="📈 Всего заявок", value=str(len(applications)), inline=True)

    if pending > 0:
        embed.add_field(name="📋 Активные заявки", value=f"Есть {pending} заявок на рассмотрение", inline=False)

    await ctx.send(embed=embed)

# ========== ЗАПУСК ==========
print("=" * 50)
print("🤖 Запуск бота BESPREDEL")
print("📋 Система заявок")
print("✅ Кнопки Принять/Отклонить")
print("🌐 24/7 работа через Flask")
print("=" * 50)

# Запускаем бота
bot.run(TOKEN)
