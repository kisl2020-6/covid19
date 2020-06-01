#!/usr/bin/ruby -Ks
# encoding: utf-8

require("cgi")
require("sqlite3")

#htmlからの入力
input = CGI.new
#データベースを参照
db = SQLite3::Database.new("mets.db")

#----------計算----------
#一日あたりの目標METs時（参照：https://www.mhlw.go.jp/stf/houdou/2r9852000002xple-att/2r9852000002xpqt.pdf）
Target_metsh = 23.0 / 7
#入力された運動のMETs時の合計値
metsh_sum = 0.0
#入力された運動の履歴配列
input_exercises = Array.new

#入力された各項目についてループ（項目番号が存在する限りループ）
i = 1
while input.has_key?("exercise" + i.to_s)
    #ExerciseIDで検索した結果
    exercise = db.execute("select * from METs where ExerciseID == ?;", input["exercise" + i.to_s]).flatten!
    #検索結果がない、検索結果が2件以上ある場合無視
    next if exercise == nil or exercise.size >= 5
    #入力された運動のデータに時間を加えて配列に格納
    exercise.push(input["time" + i.to_s])
    input_exercises.push(exercise)
    #合計METs時加算
    metsh_sum += exercise[1].to_f * input["time" + i.to_s].to_f / 60
    #次の項目番号
    i += 1
end

db.close

#条件を満たす最小のものを取り出したい
def suggest_exercise(category, metsh_diff)
    a = db.execute("select ExerciseID, MIN(METs), Category, Exercise from METs where METs >= ? and Category == ?", metsh_diff, category)
    return a
end

#----------表示----------

print("Content-type: text/html; charset=UTF-8\n\n")
print("<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML .01//EN'\n")
print("    'http://www.w3.org/TR/html14/strit.dtd'>\n")
print("<html>\n")
print("  <head>\n")
print("    <meta charset='UTF-8'>\n")
print("    <title>診断結果</title>\n")
print("    <link rel='stylesheet' href='style.css'>")
print("  </head>\n")
print("  <body>\n")
print metsh_sum
print(" / ")
print Target_metsh
print("\n<ul>\n")
input_exercises.each do |exercise|
    printf("<li>ID:%s, METs:%s, Category:%s, Exercise:%s, Time: %s</li>\n", exercise[0], exercise[1], exercise[2], exercise[3], exercise[4])
end
print("</ul>\n")
print("  </body>\n")
print("</html>\n")