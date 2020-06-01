# encoding: utf-8

require("sqlite3")

data = Array.new
#データベース
db = SQLite3::Database.new("mets.db")

#運動METs表のCSVをハッシュに格納
File.open(ARGV[0], "r:utf-8") do |f|
    f.each_line do |line|
        row = line.chomp.split(",")
        #キー：コード、値：[METs, カテゴリ, 活動]
        data.push([row[0], row[1], row[2], row[3]])
    end
end

p data

db.execute("CREATE TABLE METs(ExerciseID int not null primary key, METs float, Category char, Exercise char);")
data.each do |row|
    db.execute("INSERT INTO METs(ExerciseID, METs, Category, Exercise) VALUES (?, ?, ?, ?);", row[0], row[1], row[2], row[3])
end
db.close