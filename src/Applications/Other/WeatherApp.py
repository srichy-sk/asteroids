import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from requests import RequestException


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter a City", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temp = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")
        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temp)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description)

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temp.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temp.setObjectName("temp")
        self.emoji_label.setObjectName("emoji_label")
        self.description.setObjectName("description")

        self.setStyleSheet("""
            QLabel, QPushButton {
                font-family: Comic Sans MS;
            }

            QLabel#city_label {
                font-size: 20px;
            }

            QLineEdit#city_input {
                font-size: 20px;
                font-family: Comic Sans MS;
            }

            QPushButton#get_weather_button {
                font-size: 20px;
                font-weight: bold;
            }

            QLabel#temp {
                font-size: 30px;
            }

            QLabel#emoji_label {
                font-size: 35px;
                font-family: Apple Color Emoji;
            }

            QLabel#description {
                font-size: 25px;
            }
        """)

        self.get_weather_button.clicked.connect(self.get_weather)

    def get_weather(self):
        city_name = self.city_input.text().strip()
        api_key = "5395e24a8883f4632d86fa1eabd3ce60"  # 🔁 Replace with your real OpenWeatherMap API key

        if not city_name:
            self.display_error("Please enter a city name.")
            return

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if str(data["cod"]) == "200":
                self.display_weather(data)

        except requests.exceptions.HTTPError as http_error:
            if response.status_code == 400:
                self.display_error("Bad Request:\nPlease Check Your Input")
            elif response.status_code == 401:
                self.display_error("Unauthorized:\nInvalid API key")
            elif response.status_code == 403:
                self.display_error("Forbidden:\nAccess Is Denied")
            elif response.status_code == 404:
                self.display_error("Not Found:\nCity Not Found")
            elif response.status_code == 500:
                self.display_error("Internal Server Error:\nPlease Try Again Later")
            elif response.status_code == 502:
                self.display_error("Bad Gateway:\nInvalid Response From Server")
            elif response.status_code == 503:
                self.display_error("Service Unavailable:\nServer is down")
            elif response.status_code == 504:
                self.display_error("Gateway Timeout:\nNo Response From Server")
            else:
                self.display_error(f"HTTP Error Occurred:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\n Check Your Internet Connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\n The Request Timed Out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too Many Redirects:\n Check The URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f'Request Error:\n{req_error}')

    def display_error(self, message):
        self.temp.setStyleSheet("font-size: 25px; color: red;")
        self.temp.setText(message)
        self.emoji_label.clear()
        self.description.clear()

    def display_weather(self, data):
        self.temp.setStyleSheet("font-size: 30px; color: black;")
        temperature_k = data["main"]["temp"]
        temperature_f = (temperature_k * 9/5) - 459.67
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]

        self.temp.setText(f'{temperature_f:.0f} °F')
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description.setText(weather_description.capitalize())

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "❄️"
        elif 701 <= weather_id <= 781:
            return "🌫️"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
