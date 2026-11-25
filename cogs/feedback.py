"""Санал хүсэлт: хэрэглэгч админд илгээнэ, админ жагсаалтаас харж хариулна."""
import time

import discord
from discord.ext import commands

from perms import is_admin
from usage import send_usage
from utils import reply

COOLDOWN = 60
MAX_OPEN = 3
GOLD = 0xF59E0B


class Feedback(commands.Cog):
    """Санал хүсэлт."""

    def __init__(self, bot):
        self.bot = bot
        self._last: dict[int, float] = {}

    async def cog_check(self, ctx):
        return ctx.guild is not None

    # ---------- хүлээн авагчид ----------
    async def _recipients(self) -> list[discord.abc.Messageable]:
        out, seen = [], set()
        ch_id = await self.bot.db.get_setting("suggest_channel")
        if ch_id:
            ch = self.bot.get_channel(ch_id)
            if ch is not None:
                return [ch]
        ids = list(await self.bot.db.list_admins())
        try:
            app = await self.bot.application_info()
            members = [m.id for m in app.team.members] if app.team else [app.owner.id]
            ids = members + ids
        except Exception:
            pass
        for uid in ids:
            if uid in seen:
                continue
            seen.add(uid)
            try:
                user = self.bot.get_user(uid) or await self.bot.fetch_user(uid)
                out.append(user)
            except Exception:
                pass
        return out

    def _embed(self, row, author=None) -> discord.Embed:
        e = discord.Embed(title=f"💌 Санал #{row['id']}", description=row["text"], color=GOLD)
        e.add_field(name="Илгээсэн", value=f"<@{row['user_id']}>", inline=True)
        e.add_field(name="Төлөв", value="⏳ Хүлээгдэж байна" if row["status"] == "open" else "✅ Хаагдсан", inline=True)
        if row["reply"]:
            e.add_field(name="Хариу", value=row["reply"][:1000], inline=False)
        return e

    # ---------- хэрэглэгч ----------
    @commands.command(name="suggest", aliases=["sanal", "санал", "huselt", "хүсэлт", "feedback", "request"])
    async def suggest(self, ctx: commands.Context, *, text: str = ""):
        """Админд санал, хүсэлт илгээх"""
        text = text.strip()
        if len(text) < 5:
            await send_usage(ctx)
            return
        if len(text) > 800:
            await reply(ctx, "❌ Хэт урт байна (дээд тал нь 800 тэмдэгт).")
            return
        now = time.time()
        wait = COOLDOWN - (now - self._last.get(ctx.author.id, 0))
        if wait > 0:
            await reply(ctx, f"⏳ {int(wait) + 1} секундын дараа дахин илгээнэ үү.")
            return
        if await self.bot.db.open_suggestions_count(ctx.author.id) >= MAX_OPEN:
            await reply(ctx, f"❌ Танд хариулаагүй {MAX_OPEN} санал байна. Админ хариултал хүлээнэ үү.")
            return
        self._last[ctx.author.id] = now
        sid = await self.bot.db.add_suggestion(ctx.author.id, ctx.guild.id, text)
        row = await self.bot.db.get_suggestion(sid)
        e = self._embed(row)
        p = ctx.clean_prefix
        e.set_footer(text=f"Хариулах: {p}sreply {sid} <хариу> · Хаах: {p}sclose {sid}")
        sent = 0
        for dest in await self._recipients():
            try:
                await dest.send(embed=e)
                sent += 1
            except Exception:
                pass
        note = "Админд очлоо." if sent else "Хадгалагдлаа, админ жагсаалтаас харна."
        await reply(ctx, f"💌 Санал **#{sid}** илгээгдлээ. {note} Хариу ирвэл танд DM-ээр очно.")

    # ---------- админ ----------
    @commands.command(name="suggestions", aliases=["sanals", "саналууд"])
    async def suggestions(self, ctx: commands.Context, which: str = ""):
        """Админ: ирсэн саналуудын жагсаалт"""
        if not await is_admin(self.bot, ctx.author):
            await reply(ctx, "❌ Зөвхөн админ.")
            return
        rows = await self.bot.db.list_suggestions(only_open=which.lower() != "all", limit=10)
        if not rows:
            await reply(ctx, "📭 Хүлээгдэж буй санал алга.")
            return
        e = discord.Embed(title="📬 Саналууд", color=GOLD)
        for r in rows:
            mark = "⏳" if r["status"] == "open" else "✅"
            e.add_field(name=f"{mark} #{r['id']} · <@{r['user_id']}>"[:256],
                        value=(r["text"][:300] + (f"\n↳ **Хариу:** {r['reply'][:200]}" if r["reply"] else "")),
                        inline=False)
        p = ctx.clean_prefix
        e.set_footer(text=f"{p}sreply <№> <хариу> · {p}sclose <№>")
        await reply(ctx, embed=e)

    @commands.command(name="sreply")
    async def sreply(self, ctx: commands.Context, sid: int = 0, *, text: str = ""):
        """Админ: саналд хариулж хаах"""
        if not await is_admin(self.bot, ctx.author):
            await reply(ctx, "❌ Зөвхөн админ.")
            return
        row = await self.bot.db.get_suggestion(sid) if sid else None
        if row is None or not text.strip():
            await send_usage(ctx)
            return
        await self.bot.db.close_suggestion(sid, ctx.author.id, text.strip())
        row = await self.bot.db.get_suggestion(sid)
        dm = "✅ Хэрэглэгчид DM очлоо."
        try:
            user = self.bot.get_user(row["user_id"]) or await self.bot.fetch_user(row["user_id"])
            await user.send(embed=discord.Embed(
                title=f"💌 Таны санал #{sid}-д хариу ирлээ",
                description=f"**Таны санал:** {row['text'][:500]}\n\n**Хариу:** {row['reply']}", color=GOLD))
        except Exception:
            dm = "⚠️ DM явсангүй (хэрэглэгч DM хаасан байж магадгүй). Хариу хадгалагдлаа."
        await reply(ctx, f"✉️ Санал #{sid} хаагдлаа. {dm}")

    @commands.command(name="sclose")
    async def sclose(self, ctx: commands.Context, sid: int = 0):
        """Админ: саналыг хариугүй хаах"""
        if not await is_admin(self.bot, ctx.author):
            await reply(ctx, "❌ Зөвхөн админ.")
            return
        if not sid or not await self.bot.db.close_suggestion(sid, ctx.author.id):
            await send_usage(ctx)
            return
        await reply(ctx, f"✅ Санал #{sid} хаагдлаа.")

    @commands.command(name="suggestchannel", aliases=["sanalchannel"])
    async def suggestchannel(self, ctx: commands.Context, channel: discord.TextChannel | None = None, off: str = ""):
        """Админ: саналууд ирэх суваг"""
        if not await is_admin(self.bot, ctx.author):
            await reply(ctx, "❌ Зөвхөн админ.")
            return
        raw = ctx.message.content.lower().split()
        if channel is None and "off" in raw:
            await self.bot.db.set_setting("suggest_channel", 0)
            await reply(ctx, "✅ Санал одоо админуудад DM-ээр очно.")
            return
        if channel is None:
            await send_usage(ctx)
            return
        await self.bot.db.set_setting("suggest_channel", channel.id)
        await reply(ctx, f"✅ Санал ирэх суваг: {channel.mention}")


async def setup(bot):
    await bot.add_cog(Feedback(bot))
