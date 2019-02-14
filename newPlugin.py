import sublime, sublime_plugin,datetime,re #必ず必要

#/
#
# 選択範囲をコメントで囲むコマンド
#
#/

class surroundCommentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        date = datetime.datetime.now()
        start = "// customize Start "+str(date.year)+"/"+str(date.month)+"/"+str(date.day)+" KOBAYASHI---------------------------------------->\n"
        end = "// customize End "+str(date.year)+"/"+str(date.month)+"/"+str(date.day)+" KOBAYASHI---------------------------------------->\n"

        for region in self.view.sel():
                if not region.empty():
                    self.view.replace(edit, region, start + self.view.substr(region) +"\n" + end)

#/
#
# 選択範囲をifで囲むコマンド
#
#/

class surroundIfCommand(sublime_plugin.TextCommand):
   def run(self, edit):
        start = "if(isset($items['q1'])){\n"
        end = "}\n"

        for region in self.view.sel():
                if not region.empty():
                    self.view.replace(edit, region, start + self.view.substr(region) +"\n" + end)


#/
#
# 選択範囲を<? ?>で囲むコマンド
#
#/

class surroundPhpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        start = "<?"
        end = "?>"

        for region in self.view.sel():
            if not region.empty():
                self.view.replace(edit, region, start + self.view.substr(region) + end)


#/
#
# debug用のコマンド
#
#/

class debugCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        start = "print 'debug start';"
        end = "print '<pre>';"
        spilited_start = "print_r("
        spilited_end = ");"
        end2 = "print '</pre>';"
        end3 = "print 'debug end';"

        for region in self.view.sel():
            if not region.empty():
                self.view.replace(edit, region, start + end + spilited_start + self.view.substr(region) + spilited_end + end2 + end3 + "\n" + self.view.substr(region) )


#/
#
# 選択範囲をpreタグで囲むコマンド
#
#/

class surroundPreCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        start = "<pre>"
        end = "</pre>"

        for region in self.view.sel():
            if not region.empty():
                self.view.replace(edit, region, start + "\n" + self.view.substr(region) +"\n" + end)


#/
#
# テーブル関連タグをハイライトするコマンド
#
#/

class tableHighlightCommand(sublime_plugin.TextCommand):
    count = 0
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                # tableタグに対応するregionを作成し、ハイライトする
                if self.count == 0:
                    self.count+=1
                    patern="<table.*>||</table>||<tr.*>||</tr>||<td.*>||</td>||<th.*>||</th>||"
                    target_regions=self.view.find_all(patern)
                    self.view.add_regions('tableHighlight', target_regions, "string","dot", sublime.DRAW_NO_FILL)
                    break
                # 再度クリックすると、登録したregionを削除する
                elif self.count == 1:
                    self.count-=1
                    self.view.erase_regions('tableHighlight')
                    break


#/
#
# 配列の構造を出力するコマンド
#
#/

class dispArrayStructureCommand(sublime_plugin.TextCommand):

#/
# tabの数を数える
#
# @return Srring
#
#/

    def countTabOnLine(self,selected_region):
        line=self.view.substr(self.view.line(selected_region))
        count=0
        for char in line:
            if char=="\t":
                count+=1
        return count

#/
# $itemsから始まるtop親要素を見つける
#
# @return Object
# Objectはそれぞれターゲットの親要素で、rowとstringを持つ
#/

    def findTopParent(self,patern,selected_region,delete_word):
        matched_regions=self.view.find_all(patern)
        filtered_matched_regions=[]
        result=[]

        for matched_region in matched_regions:
            if selected_region.begin()-matched_region.begin()>=0 and selected_region.end()-matched_region.end()>=0:
                filtered_matched_regions.append(matched_region)

# resionに近い順にソートする
        filtered_matched_regions.reverse()
        firstCloseObject=Object()
        firstCloseObject.row, col1=self.view.rowcol(filtered_matched_regions[0].begin())
        firstCloseObject.string=self.view.substr(filtered_matched_regions[0]).replace(delete_word, "")

        return firstCloseObject


#/
# top以外の親要素を見つける
#
# @return Array(Object,Object,...)
# Objectはそれぞれターゲットの親要素で、rowとstringを持つ
#/

    def findParents(self,patern,selected_region,delete_word,tabCnt):

        result=[]
        new_patern=""
# タブの数を1～増やしながら探していく
        for i,j in enumerate(range(1,tabCnt)):
            # print(j)
            new_patern="^"+"\t" * j + patern

            matched_regions=self.view.find_all(new_patern)
            filtered_matched_regions=[]

            result.append(self.findCloseParent(selected_region,delete_word,matched_regions))
        return result


#/
# 一番近い親要素ひとつを見つける
#
# @return Object
# Objectはターゲットの親要素で、rowとstringを持つ
#/

    def findCloseParent(self,selected_region,delete_word,matched_regions):
        filtered_matched_regions=[]

        for matched_region in matched_regions:
            if selected_region.begin()-matched_region.begin()>=0 and selected_region.end()-matched_region.end()>=0:
                filtered_matched_regions.append(matched_region)

# regionに近い順にソートする
        filtered_matched_regions.reverse()

        firstCloseObject=Object()
        firstCloseObject.row, col1=self.view.rowcol(filtered_matched_regions[0].begin())
        firstCloseObject.string=self.view.substr(filtered_matched_regions[0]).replace(delete_word, "")
        firstCloseObject.string=re.findall('[a-zA-Z0-9]+',firstCloseObject.string)

        return firstCloseObject





    def run(self, edit):
        selected_regions=self.view.sel()
        selected_region=selected_regions[0]
        parent=""
        result=""
        close_parent=""
        selected_word=""
        cp=""
        pa=""

        tabCnt = self.countTabOnLine(selected_region)

        selected_word=self.view.substr(selected_region)
        topParent=self.findTopParent("\$.* = array",selected_region," = array")

        close_parents=self.findParents("\'[a-zA-Z0-9]*\' => array\(",selected_region," => array(",tabCnt)

        result+=topParent.string


        for close_parent in close_parents:
            print(close_parent.string[0])
            result+="['{}']".format(close_parent.string[0])

        result+="['{}']".format(selected_word.replace("'",""))


        sublime.set_clipboard(result)

        window = self.view.window()
        output_view = window.create_output_panel("WindowName")
        window.run_command("show_panel", {"panel":"output.WindowName"})

        output_view.set_read_only(False)
        output_view.insert(edit, output_view.size(), result)
        output_view.set_read_only(True)
        sublime.message_dialog(result)


class Object:
    row=""
    string=""



class surroundSpaceCommand(sublime_plugin.TextCommand):

   # 位置を用いる案
    # １行に複数マッチする場合
    # イコール関連としては、!=や文字列の""なども考えられる
    # 何回か押す必要がある（元のインデックスからはみでてしまうため）


    # def insertLine(self, edit, line):
    #     ln=self.view.substr(line)
    #     position_=ln.find("=")
    #     if position_!=-1:
    #         is_ls_3equal = ln[position_+1]=="=" and ln[position_+2]=="=" and ln[position_+3]!=" "
    #         is_rs_3equal = ln[position_+1]=="=" and ln[position_+2]=="=" and ln[position_-1]!=" "

    #         is_ls_2equal = ln[position_+1]=="=" and ln[position_+2]!=" " and ln[position_+2]!="=" and ln[position_-1]!="="
    #         is_rs_2equal = ln[position_+1]=="=" and ln[position_-1]!=" " and ln[position_+2]!="=" and ln[position_-1]!="="

    #         is_ls_not_equal = ln[position_-1]=="!" and ln[position_+1]!=" "
    #         is_rs_not_equal = ln[position_-1]=="!" and ln[position_-2]!=" "


    #         is_ls_equal = ln[position_+1]!=" " and ln[position_+1]!="=" and not (is_ls_2equal or is_rs_2equal) and not (is_ls_3equal or is_rs_3equal) and not(is_ls_not_equal or is_rs_not_equal)
    #         is_rs_equal = ln[position_-1]!=" " and ln[position_+1]!="=" and not (is_ls_2equal or is_rs_2equal) and not (is_ls_3equal or is_rs_3equal) and not(is_ls_not_equal or is_rs_not_equal)


    #         if is_ls_3equal:
    #             self.view.insert(edit, line.begin()+position_+3, " ")
    #         if is_rs_3equal:
    #             self.view.insert(edit, line.begin()+position_, " ")
    #         if is_ls_2equal:
    #             self.view.insert(edit, line.begin()+position_+2, " ")
    #         if is_rs_2equal:
    #             self.view.insert(edit, line.begin()+position_, " ")
    #         if is_ls_not_equal:
    #             self.view.insert(edit, line.begin()+position_+1, " ")
    #         if is_rs_not_equal:
    #             self.view.insert(edit, line.begin()+position_-1, " ")
    #         if is_ls_equal:
    #             self.view.insert(edit, line.begin()+position_+1, " ")
    #         if is_rs_equal:
    #             self.view.insert(edit, line.begin()+position_, " ")

    # def run(self, edit):
    #     for region in self.view.sel():
    #         if not region.empty():
    #             lines=self.view.lines(region)
    #             i = 1
    #             for line in lines:
    #                 self.insertLine(edit, line)

    def pregInsert(self, edit):
        print("pregInsert始まり")
        patern="===|!==|==|<=|!=|\+\+|=|\+|\-|\*|\%|>"
        i = 0
        matched_regions=self.view.find_all(patern)
        print(matched_regions)
        for matched_region in matched_regions:
            print(self.view.substr(matched_region))
            before_string = self.view.substr(sublime.Region(matched_region.begin()+i - 1,matched_region.begin()+i ))
            after_string = self.view.substr(sublime.Region(matched_region.end()+i,matched_region.end()+i + 1))

            print(before_string, after_string)
            if before_string != " ":
                self.view.insert(edit, matched_region.begin()+i, " ")
                i = i + 1
            if after_string != " ":
                self.view.insert(edit, matched_region.end() + i, " ")
                i = i + 1

    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                    self.pregInsert(edit)
