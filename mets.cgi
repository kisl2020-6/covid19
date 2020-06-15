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
    exercise = db.execute("select * from Exercises where ExerciseID == ?;", input["exercise" + i.to_s]).flatten!
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

#提案された運動を格納する配列
suggested_exercises = Array.new

#指定したカテゴリの中で、指定したMETsよりも大きい最小の項目を取り出す関数
def suggest_exercise(db, target_mets, category)
    result = db.execute("select * from Exercises where METs >= ? and Category == ? and \
        METs = (select min(METs) from Exercises where METs >= ? and Category = ?)", target_mets, category, target_mets, category)[0]
    #結果がなければ一番高いやつ入れとく
    result = db.execute("select * from Exercises where Category = ? and \
        METs = (select max(METs) from Exercises where Category = ?)", category, category)[0] if result == nil
    return result
end

#METs時が目標より不足しているとき、それを補う運動を各カテゴリから提案する
if Target_metsh > metsh_sum
    #目標より不足しているMETs時
    metsh_diff = Target_metsh - metsh_sum
    #「運動、筋トレなど」カテゴリ。10分＝1/6時間行うよう提案する。
    suggested_exercises.push(suggest_exercise(db, metsh_diff * 6, "運動、筋トレなど").push(10))
    #「家事」カテゴリ。20分＝1/3時間行うよう提案する。
    suggested_exercises.push(suggest_exercise(db, metsh_diff * 3, "家事").push(20))
    #「外出時」カテゴリ。30分＝1/2時間行うよう提案する。
    suggested_exercises.push(suggest_exercise(db, metsh_diff * 2, "外出時").push(30))
    #「趣味」カテゴリ。60分＝1/1時間行うよう提案する。
    suggested_exercises.push(suggest_exercise(db, metsh_diff, "趣味").push(60))
    suggested_exercises.push(db.execute("select * from Exercises where ExerciseID == ?;", rand(1..30)).flatten!.push(60))
    suggested_exercises.push(db.execute("select * from Exercises where ExerciseID == ?;", rand(1..30)).flatten!.push(60))
end

#----------表示----------

print("Content-type: text/html; charset=UTF-8\n\n")
print("<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML .01//EN'\n")
print("    'http://www.w3.org/TR/html14/strit.dtd'>\n")
print("<html>\n")
print("  <head>\n")
print("    <meta charset='UTF-8'>\n")
print("    <title>診断結果</title>\n")
print("    <link rel='stylesheet' href='style.css'>\n")
print("  </head>\n")
print("  <body>\n")
print("    <div class='container'>\n")
print("    <input type='checkbox' id='acd_check1' class='acd_check' checked />\n")
print("    <label for='acd_check1' class='acd_label'>\n")
print("      <div class='gauge'>\n")
printf("        <div class='gauge_progress' style='width:%s%%'></div>\n", metsh_sum / Target_metsh * 100)
print("      </div>\n")
print("    </label>\n")
print("    <div id='acd_content1' class='acd_content'>\n")
printf("      <h3>一日あたり <span class='achieve'>%s</span> / %.2f METs時<br />\n", metsh_sum, Target_metsh)
printf("      ※一週間あたり <span class='achieve'>%.2f</span> / 23 METs時</h3>\n", metsh_sum * 7)
print("      <ul>\n")
input_exercises.each do |exercise|
    printf("        <li>%s：　%s METs　×　%s 分　＝　%.2f METs時</li>\n", exercise[3], exercise[1], exercise[4], exercise[1].to_f * exercise[4].to_i / 60)
end
print("      </ul><br />\n")
print("      <div class='footer'>\n")
print("        健康維持のためには「強度が3METs以上の運動を一週間あたり23METs時以上行う」という基準が示されています<br />\n")
print("        （参照：<a href='https://www.mhlw.go.jp/stf/houdou/2r9852000002xple-att/2r9852000002xpqt.pdf'>https://www.mhlw.go.jp/stf/houdou/2r9852000002xple-att/2r9852000002xpqt.pdf</a>）\n")
print("      </div>\n")
print("    </div>\n")
if Target_metsh > metsh_sum
    print("    <h2>健康維持のために、もうすこしだけ運動してみましょう！</h2>\n")
    print("    例えば、今からこんな運動はいかがですか？<br />\n")
    print("    <div class='boxes'>\n")
    suggested_exercises.each do |exercise|
        printf("      <a href='https://www.google.com/search?q=memo:%s+%s分' target='_blank'><div class='suggestion' style='background-image: url(\"img/%s.jpeg\");' ontouchstart=''>\n", exercise[3], exercise[4], exercise[0])
        printf("        <p>%s<br />（%sMETs）を <span class='achieve'>%s</span> 分</p>\n",  exercise[3], exercise[1], exercise[4])
        print("      </div></a>\n")
    end
    print("    </div>\n")
else
    print("    <h2>健康維持のために必要な運動は足りているようです！</h2>\n")
    print("    この調子です。健康維持のために運動を続けていきましょう\n")
end
print("    </div>\n")
print("  </body>\n")
print("</html>\n")

db.close
