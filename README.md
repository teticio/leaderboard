# leaderboard
Create a bar chart race in realtime from a Kaggle leaderboard

You can create a bar chart race project for free in Flourish https://app.flourish.studio/@flourish/bar-chart-race.

Then run this script
`python leaderboard kaggle-competition-name --user flourish-user-name --password flourish-password --project flourish-project-number`

Under the hood it uses the Kaggle API to download the leaderboard data (`pip install kaggle` and store your credentials in `~/.kaggle/kaggle.json`) and Selenium to upload the data with Chrome (`pip install selenium` and save the appropriate `chromedriver` on your `PATH` from https://chromedriver.chromium.org/downloads). By default it will do this every 5 minutes, but you can configure this with the optional `--every` parameter.

![](https://github.com/teticio/leaderboard/blob/master/Global%20Wheat%20Detection%20-%20Kaggle%20competition.png?raw=true)
