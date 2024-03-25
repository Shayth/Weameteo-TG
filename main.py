import datetime
import requests
import telebot
import time

from api_keys import openweather_api_key, tg_bot_token

bot = telebot.TeleBot(tg_bot_token)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Приветствую!\nНапишите полное название города, и я отправлю вам данные о погоде')


@bot.message_handler(content_types=['text'])
def get_weather(message):
    city_name = message.text
    r = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={openweather_api_key}&units=metric&lang=ru')
    if r.status_code == 200:
        accepted_data = r.json()
        city = accepted_data['name']
        temperature = accepted_data['main']['temp']
        feel_temp = accepted_data['main']['feels_like']
        weather = accepted_data['weather'][0]['description']
        wind_speed = accepted_data['wind']['speed']
        pressure = accepted_data['main']['pressure'] * 0.75
        humidity = accepted_data['main']['humidity']
        timezone = accepted_data['timezone']
        rr = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={openweather_api_key}&units=metric&lang=ru')
        forecast_data = rr.json()
        forecast_lst = []
        default_time_forecast = '12:00:00'
        for i in forecast_data['list']:
            forecast = [(i['dt_txt']+" "+'{0:+3.0f}'.format(i['main']['temp']))]
            for i in forecast:
                if default_time_forecast in i:
                    forecast_str = i.replace('12:00:00', '')
                    forecast_lst.append(forecast_str+'\n')

        crnt_timezone = 10800
        timeform = '%d-%m-%Y %H:%M'
        timeshift = timezone - crnt_timezone
        crnt_time = datetime.datetime.now() + datetime.timedelta(seconds=timeshift)
        bot.reply_to(message, f"Город: {city}\n"f"Местное время: {crnt_time.strftime(timeform)}\n"
                     f"Температура: {temperature} C°\nОщущается как: {feel_temp}C°\n"
                     f"Текущая погода: {weather.capitalize()}\nСкорость ветра: {wind_speed} м/с\n"
                     f"Давление: {round(pressure, 1)} мм.рт.ст\nВлажность: {humidity}%\n"
                     f"Прогноз погоды:\n{''.join(forecast_lst)}"
                     )
    else:
        bot.reply_to(message, "Город не найден.")


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            print(e)
# bot.polling(none_stop=True)
