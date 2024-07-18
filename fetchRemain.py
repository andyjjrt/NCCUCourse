import logging

import requests
from bs4 import BeautifulSoup

PROPERTY_NAME = {
    "專業基礎(開放系所)人數": "origin",
    "其他系所": "otherDept",
    "總人數": "all",
    "本系本班Dept./Class": "origin",
    "本系非本班同年級Other Classes in Dept., Same Year": "sameGrade",
    "本系非本班不同年級Other Classes in Dept., Dif. Year": "diffGrade",
    "輔系Minor": "minor",
    "雙主修Double-Major": "doubleMajor",
    "全系Dept.": "origin",
    "本院非本系Other Depts. in the College": "otherDeptInCollege",
    "非本院Other Colleges": "otherCollege",
    "學分學程": "program",
    "全校All Colleges": "all",
    "本學程開課年級（含）以上Same Year (and above) in the Program": "sameGradeAndAbove",
    "本學程其他低年級Year Below you in the Program": "lowerGrade",
    "本院非學程限制人數Maximum Limits for Other Programs in the College": "otherProgram",
    "外院限制人數Maximum Limits for Other Colleges": "otherCollege",
    "總限制人數Overall Maximum Limits": "all",
}
ROW_NAME = {
    "限制人數 / Maximum limit": "Limit",
    "選課人數 / Number Registered": "Registered",
    "餘額 / Number of Available Spaces": "Available"
}


def fetchRemain(fetch_url: str):
    result = {prop+row: None for prop in PROPERTY_NAME.values() for row in ROW_NAME.values()}

    try:
        response = requests.get(fetch_url.replace("https://", "http://"))
        response.raise_for_status()

        soap = BeautifulSoup(response.content, "html.parser")
        
        table = soap.find("div", {"class": "maintain_profile_content_table"}).find_all("tr")
        open_to_signable_adding = table[5].find_all("td")[1].text
        result["signableAdding"] = True if open_to_signable_adding == "是" else False
        
        number_on_waiting_list = table[6].find_all("td")[1].find("a").text
        result["waitingList"] = int(number_on_waiting_list) if number_on_waiting_list.isdigit() else number_on_waiting_list
        
        table = soap.find("table", {"id": "tclmtcntGV"}).find_all("tr")
        for _, prop in enumerate(table[0]):
            if prop.get_text(strip=True) != "":
                for row in table[1:]:
                    cells = row.find_all("td")
                    for td in cells:
                        result[PROPERTY_NAME[prop.text] + ROW_NAME[cells[0].text]] = int(td.text) if td.text.isdigit() else td.text
    except Exception as e:
        logging.error(e)

    return result


if __name__ == "__main__":
    print(fetchRemain(
        "https://selectcourse.nccu.edu.tw/remain/goGenDetail.aspx?view=7735414C415774495851503054646C41713573494F513D3D"))
