@echo off


mkvmerge ^
	--chapters "chapters.xml" ^
	--global-tags "tags.xml" ^
	--disable-track-statistics-tags ^
	-o "test.mkv" ^
	^
	--no-chapters --no-global-tags ^
	-A -S -B -T -M ^
	--language "-1:eng" ^
	--track-name "-1:Test Video" ^
	--default-track -1 ^
	"source.mkv" ^
	^
	--no-chapters --no-global-tags ^
	-D -S -B -T -M ^
	--language "-1:eng" ^
	--track-name "-1:Test Audio" ^
	--default-track -1 ^
	"source.aac" ^
	^
	--no-chapters --no-global-tags ^
	-A -D -B -T -M ^
	--sub-charset "-1:UTF-8" ^
	--language "-1:eng" ^
	--track-name "-1:Test Subtitles" ^
	"subtitles.ass" ^
	^
	--attachment-name "Verdana Bold" ^
	--attachment-description "Test font attachment" ^
	--attachment-mime-type "application/x-font-ttf" ^
	--attach-file "verdanab.ttf"


mkvmerge ^
	--disable-track-statistics-tags ^
	--webm ^
	-o "test.webm" ^
	^
	--no-chapters --no-global-tags ^
	-A -S -B -T -M ^
	--language "-1:eng" ^
	--track-name "-1:Test Video" ^
	--default-track -1 ^
	"source.webm" ^
	^
	--no-chapters --no-global-tags ^
	-D -S -B -T -M ^
	--language "-1:eng" ^
	--track-name "-1:Test Audio" ^
	--default-track -1 ^
	"source.ogg"

