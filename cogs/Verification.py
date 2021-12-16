import asyncio
import logging
import os
import random
import shutil
import string
from utils.config import Config
import Augmentor
import discord
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from discord.ext import commands
from utils.mongodb import guild_settings
from utils.logger import logger

config = Config()


class Verification(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = await guild_settings.find_one({"_id": int(member.guild.id)})
        settings = settings["settings"]
        if member.bot:
            return
        if settings["Verification"]["Status"]:
            memberTime = f"{member.joined_at.year}-{member.joined_at.month}-{member.joined_at.day} {member.joined_at.hour}:{member.joined_at.minute}:{member.joined_at.second}"
            image = np.zeros(shape=(100, 350, 3), dtype=np.uint8)

            image = Image.fromarray(image + 255)

            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font="./locales/fonts/Roboto-Black.ttf", size=60)

            text = ' '.join(
                random.choice(string.ascii_uppercase) for _ in range(6))

            W, H = (350, 100)
            w, h = draw.textsize(text, font=font)
            draw.text(((W - w) / 2, (H - h) / 2), text, font=font, fill=(90, 90, 90))

            ID = member.id
            folderPath = f"locales/img/captchaFolder/captcha_{ID}"
            try:
                os.mkdir(folderPath)
            except:
                if os.path.isdir('locales/img/captchaFolder') is False:
                    os.mkdir("locales/img/captchaFolder")
                if os.path.isdir(folderPath) is True:
                    shutil.rmtree(folderPath)
                os.mkdir(folderPath)
            image.save(f"{folderPath}/captcha{ID}.png")

            p = Augmentor.Pipeline(folderPath)
            p.random_distortion(probability=1, grid_width=4, grid_height=4, magnitude=14)
            p.process()

            path = f"{folderPath}/output"
            files = os.listdir(path)
            captchaName = [i for i in files if i.endswith('.png')]
            captchaName = captchaName[0]

            image = Image.open(f"{folderPath}/output/{captchaName}")

            width = random.randrange(6, 8)
            co1 = random.randrange(0, 75)
            co3 = random.randrange(275, 350)
            co2 = random.randrange(40, 65)
            co4 = random.randrange(40, 65)
            draw = ImageDraw.Draw(image)
            draw.line([(co1, co2), (co3, co4)], width=width, fill=(90, 90, 90))

            noisePercentage = 0.25

            pixels = image.load()
            for i in range(image.size[0]):
                for j in range(image.size[1]):
                    rdn = random.random()
                    if rdn < noisePercentage:
                        pixels[i, j] = (90, 90, 90)

            image.save(f"{folderPath}/output/{captchaName}_2.png")

            captchaFile = discord.File(f"{folderPath}/output/{captchaName}_2.png")

            tries = 3

            channel = self.client.get_channel(int(settings["Verification"]["channel"]))
            captcha_embed = await channel.send(
                f"**DU MUSST DIESE CAPTCHA EINGEBEN UM DEM SERVER BEIZUTRETEN:**\nBitte {member.mention}, gebe die Captcha ein um Zugriff auf den Ganzen Server zu erhalten(nur 6 Großbuchstaben).",
                file=captchaFile)

            while tries > 0:

                def check(m):
                    if m.author.id == member.id and m.content != "":
                        return m.content

                try:
                    msg = await self.client.wait_for('message', timeout=120.0, check=check)

                    password = text.split(" ")
                    password = "".join(password)
                    if msg.content == password:
                        embed = discord.Embed(description=f"{member.mention} hat die Captcha bestanden.",
                                              color=discord.Color.green())
                        await channel.send(embed=embed)
                        try:
                            role = discord.utils.get(member.guild.roles,
                                                     id=int(settings["Verification"]["role"]))
                            await member.add_roles(role)
                        except Exception as error:
                            logging.error(f"Give and remove roles failed : {error}")
                        if settings["Log"]["Status"] is not False:
                            channel = self.client.get_channel(int(settings["Log"]["channel"]))
                            embed = discord.Embed(description=f"{member.name} hat die Captcha bestanden.",
                                                  color=discord.Color.green())
                            await channel.send(embed=embed)
                        return
                    if msg.content != password:
                        if tries == 1:
                            tries -= 1
                            tries += 3
                            embed = discord.Embed(
                                description=f"{member.name} hat die Captcha nicht bestanden.\n Du hast einen weiteren versuch oder du wirst gekickt.",
                                color=discord.Color.red())
                            await channel.send(embed=embed)
                            if settings["Log"]["Status"]:
                                channel = self.client.get_channel(int(settings["Log"]["channel"]))
                                embed = discord.Embed(title=f"Captcha got Failed by {member.name}",
                                                      color=int(config.colorMain, 16),
                                                      description=f"{member.name} wurde gekickt, da er die Captcha 3 mal nicht bestanden hat.")
                                await channel.send(embed=embed)
                            await member.kick(reason="hat die Captcha nicht bestanden")
                            return
                        if tries != 1:
                            embed = discord.Embed(
                                description=f"{member.name} hat die Captcha nicht bestanden.\n Du hast weitere **{tries}** Versuche.",
                                color=int(config.colorMain, 16))
                            await channel.send(embed=embed)
                            tries -= 1



                except asyncio.TimeoutError:
                    embed = discord.Embed(title=f"**TIME IS OUT**",
                                          description=f"{member.mention} die Antwortzeit ist abgelaufen (120s).",
                                          color=0xff0000)
                    await channel.send(embed=embed, delete_after=5)
                    try:
                        link = await channel.create_invite(max_age=172800)
                        embed = discord.Embed(title=f"**YOU HAVE BEEN KICKED FROM {member.guild.name}**",
                                              description=f"Reason : die Antwortzeit ist abgelaufen (120s) : <{link}>",
                                              color=int(config.colorMain, 16))
                        await member.send(embed=embed)
                        await member.kick(
                            reason=f"Reason : Die Antwortzeit ist abgelaufen (120s)\n\nUser Informationen :\n\nName : {member}\nId : {member.id}")
                    except Exception:
                        pass

                    await asyncio.sleep(3)
                    await captcha_embed.delete()

                    if settings["Log"]["Status"]:
                        channel = self.client.get_channel(int(settings["Log"]["channel"]))
                        embed = discord.Embed(title=f"**{member} wurde gekickt.**",
                                              description=f"**Reason :** Die Antwortzeit ist abgelaufen (120s).\n\n**__User Informationen :__**\n\n**Name :** {member}\n**Id :** {member.id}",
                                              color=int(config.colorMain, 16))
                        embed.set_footer(text=f"at {memberTime}")
                        await channel.send(embed=embed)

            try:
                await asyncio.sleep(5)
                shutil.rmtree(folderPath)
            except Exception as error:
                logger.error(f"Delete captcha file failed {error}")


def setup(client):
    client.add_cog(Verification(client))
