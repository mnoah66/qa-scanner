import datetime as dt
from collections import defaultdict
import time
import collections
import operator
import pandas as pd
import csv
import sys
import config
import string
from pathlib import Path
from mailtest import sendEmail

def get_truth(inp, relate, cut):
    ops = {'>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '=': operator.eq,
        '!=': operator.ne}
    return ops[relate](inp, cut)
def name_checker(scan_data, results_list, *args):
    def gimmeFirst(s):
        for k, v in s.items(): # K = "Clearview", v = ["Smith, Jane", "Yo, Ay"]
            namesList = []
            for n in v:
                x = n.split(',')
                fname = x[1].strip()
                if '\"' in fname:
                    b = fname.split(' ')
                    alias = re.findall('"([^"]*)"', b[1]) # Extract the alias from double quotes
                    namesList.append(alias[0].lower())
                    namesList.append(b[0].strip().lower())
                else:
                    namesList.append(fname.lower())
            s[k]=namesList
        return s
    #names = [x[2] for x in scan_data] # THis is giving ALL names, so Warbasse is being checked against Sparta names.  it should only do a check for names of individuals in that program.
    def programNames(scan_data):
      people = {}
      for item in scan_data:
        if item[4] not in people: #Program
          people[item[4]] = []
        if item[2] not in people[item[4]]:
          people[item[4]].append(item[2])
      return people #dict

    nameProgramMap = programNames(scan_data)
    firstNames = gimmeFirst(nameProgramMap)
    #print(firstNames) #{}'Clearview (GH1038)': ['Steven', 'Jewan', 'Samuel', 'Mark']}
    '''
    for item in scan_data:
        note = item[1].lower().translate(str.maketrans('','',string.punctuation)).split()
        for name in firstNames:
            if name.lower() not in item[2].lower() and name.lower() in note:
                l,s,r = item[1].lower().partition(name.lower())
                msg = "NAME CHECKER: Found " + '\"' + name +'\"'+ " in " + item[2] + "\'s note"
                note = l+ s.upper() + r
                results_list.append([item[0], msg, item[2], str(item[3].strftime('%m/%d/%Y')),
                        item[4],note, item[5].strftime("%I:%M %p"), item[6].strftime("%I:%M %p"), item[7], item[8]])
                break
    '''
    for item in scan_data:
        note = item[1].lower().translate(str.maketrans('','',string.punctuation)).split()
        for k, v in firstNames.items():
            if item[4] == k:
                for name in v:
                #Pseudo-code
                # In Jewans Note: Mark did this and that.
                #if item[2].lower() in firstNames[item[4]] and
                    if name.lower() not in item[2].lower() and name.lower() in note:
                        l,s,r = item[1].lower().partition(name.lower())
                        msg = "NAME CHECKER: Found " + '\"' + name +'\"'+ " in " + item[2] + "\'s note"
                        note = l+ s.upper() + r
                        results_list.append([item[0], msg, item[2], str(item[3].strftime('%m/%d/%Y')),
                                item[4],note, item[5].strftime("%I:%M %p"), item[6].strftime("%I:%M %p"), item[7], item[8]])
                        break
def noteLength(scan_data, results_list, *args):
    for item in scan_data:
        if item[10] == "Individual Supports" and len(item[1]) < config.notelength:
            results_list.append([item[0],'NOTE LENGTH < ' + str(config.notelength), item[2], item[3].strftime('%m/%d/%Y'),
                item[4], item[1], item[5].strftime("%I:%M %p"), item[6].strftime("%I:%M %p"), item[7], item[8]])
def noteType(scan_data, results_list, *args):
    for item in scan_data:
        if item[15] != "Service/Treatment Plan Linked" and item[15] != "Admin Support":
            results_list.append([item[0],'NOTE TYPE= {0}'.format(item[15]), item[2], item[3].strftime('%m/%d/%Y'),
                item[4], item[1], item[5].strftime("%I:%M %p"), item[6].strftime("%I:%M %p"), item[7], item[8]])
def svcType(scan_data, results_list, *args):
    billableServices = ['Individual Supports', "Transportation", "Behavioral Supports - Assessment/Plan Development", "Physical Therapy - Individual", ]
    for item in scan_data:
        if item[10] not in billableServices:
            results_list.append([item[0],'SERVICE TYPE={0}.  This is not a valid, billable service.'.format(item[10]), item[2], item[3].strftime('%m/%d/%Y'),
                item[4], item[1], item[5].strftime("%I:%M %p"), item[6].strftime("%I:%M %p"), item[7], item[8]])

def eSigned(scan_data, results_list, *args):
    for item in scan_data:
        if item[16] == "No":
            results_list.append([item[0],'UNSIGNED NOTE'.format(item[10]), item[2], item[3].strftime('%m/%d/%Y'),
                item[4], item[1], item[5].strftime("%I:%M %p"), item[6].strftime("%I:%M %p"), item[7], item[8]])
def missingForm(scan_data, results_list, *args):
    for item in scan_data:
        if item[10] == "Individual Supports" and item[18] != "Progress Note - Residential":
            results_list.append([item[0],'FORM={0}'.format(item[18]), item[2], item[3].strftime('%m/%d/%Y'),
                item[4], item[1], item[5].strftime("%I:%M %p"), item[6].strftime("%I:%M %p"), item[7], item[8]])
def duplicate_notes(scan_data, reports_list, *args):
    my_list = []
    for item in scan_data:
        my_list.append((str(item[2]), item[3],item[5]))
    seen = {}
    dupes = []
    for x in my_list:
        if x not in seen:
            seen[x] = 1
        else:
            if seen[x] == 1:
                dupes.append(x)
            seen[x] += 1
    for x in dupes:
        reports_list.append(['DUPLICATED NOTE/START TIMES',"{0} has duplicated start times ({1}) on {2}".format(x[0], x[2].strftime('%I:%M %p'),
                            x[1].strftime('%m/%d/%y')),x[1].strftime('%m/%d/%y'),nameProgramRes[x[0]],'','','','','',''])

        #reports_list.append(['DUPLICATED START TIME', "{0} has duplicated start times ({1}) on {2}".format(x[0], x[2].strftime('%I:%M %p'),
    #                        x[1].strftime('%m/%d/%y')),\
#                            '','','','','','','',''])
    #del my_list
    #del seen
    #del dupes

def duplicate_content(scan_data, results_list, *args):
    notes=[]
    for item in scan_data:
        if item[4] != 'Employment Connections (SE2102)':
            notes.append(item[1])
    dupnotes = [item for item, count in collections.Counter(notes).items() if count > 1]
    for item in dupnotes:
        iterdata = iter(scan_data)
        next(iterdata)
        for n in iterdata:
            if item == n[1]:
                results_list.append([n[0],'DUPLICATED NOTE',n[2],n[3].strftime('%m/%d/%Y'),
                    n[4], n[1], n[5].strftime("%I:%M %p"), n[6].strftime("%I:%M %p"), n[7], n[8]])


def timeModified(scan_data, reports_list, *args):
    for item in scan_data:
        # First, check if Date Modified == Contact Date
        if item[13] == item[3]:
            modifiedDelta = dt.timedelta(hours=item[14].hour, minutes=item[14].minute, seconds=item[14].second)
            endDelta = dt.timedelta(hours=item[6].hour, minutes=item[6].minute, seconds=item[6].second)
            diff = endDelta - modifiedDelta
            if (endDelta > modifiedDelta) and (diff.seconds //60 > float("2") * 60):
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                minutes = (diff.seconds %3600) // 60

                results_list.append([item[0],'TIME MODIFIED - {a} HOURS OR MORE BEFORE END TIME'.format(a=str(2))+
                "Note on {b} ({f} - {g}) last modified at {c} on {d} ({hours} hour(s) {minutes} before End Time)".format(

                    b=str(item[3].strftime('%m/%d/%Y')),
                    c=item[14].strftime("%I:%M %p"),
                    d=item[13].strftime('%m/%d/%Y'),
                    g=item[6].strftime("%I:%M %p"),
                    f=item[5].strftime("%I:%M %p"),
                    hours=str(hours),
                    minutes=str(minutes)
                    ),item[2], item[3].strftime('%m/%d/%Y'),
                        item[4], item[1], item[5].strftime("%I:%M %p"), item[6].strftime("%I:%M %p"), item[7], item[8]])
                #results_list.append([item[0], ])
        # Credit to mulagala:
        # https://stackoverflow.com/questions/24217641/how-to-get-the-difference-between-two-dates-in-hours-minutes-and-seconds
        contact = dt.datetime.combine(item[3], item[6])

        modified = dt.datetime.combine(item[13], item[14])

        diff = modified - contact

        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600

        if hours > int(24): #  Grab how many hours the user wants to flag.
            results_list.append([item[0],'NOTE MODIFIED - {0} HOURS OR MORE AFTER'.format(str(24)) + \
                "{a}'s note on {b} ({h} - {g}) was last modified at {c} on {d} ({e} day(s) {f} hours after)". \
                    format(
                            a=item[2],
                            b=str(item[3].strftime('%m/%d/%Y')),
                            c=item[14].strftime("%I:%M %p"),
                            d=item[13].strftime('%m/%d/%Y'),
                            e=str(diff.days),
                            f=str(diff.seconds//3600),
                            g=item[6].strftime("%I:%M %p"),
                            h=item[5].strftime("%I:%M %p")
                            ), item[2], item[3].strftime('%m/%d/%Y'),
                                item[4], item[1], item[5].strftime("%I:%M %p"), item[6].strftime("%I:%M %p"), item[7], item[8]])

def record_count(scan_data, reports_list, recordCount,*args):
    people = defaultdict(dict)
    for item in scan_data:
        if item[4] != "Supervised Apartments (SA1509)":

            if item[2] not in people: #Name
                people[item[2]] = defaultdict(dict)
            if item[4] not in people[item[2]][item[3]]: #If program is not in name:date
                people[item[2]][item[3]][item[4]] = []
            people[item[2]][item[3]][item[4]].append(item[7])
    for k, v in people.items(): #K is Martin Noah
        for key, val in v.items(): #Key is the date, val is the list
            for x, y in val.items():
                if len(y) < int(recordCount):
                    reports_list.append(["LESS THAN 3 PROGRESS NOTES","PN's < " + str(recordCount) + f': {k} has less than {recordCount} notes on {key.strftime("%m/%d/%Y")}.  If worked double, please split notes.',key.strftime("%m/%d/%Y"),x,'','','','','',''])
                    break
                    #reports_list.append(['DUPLICATED NOTE/START TIMES',"{0} has duplicated start times ({1}) on {2}".format(x[0], x[2].strftime('%I:%M %p'),
                    #                    x[1].strftime('%m/%d/%y')),x[1].strftime('%m/%d/%y'),nameProgramRes[x[0]],'','','','','',''])


def csvWritee(d, rp, outputWriter):
    for k, item in d.items():
        outputWriter.writerow([k,'; '.join(item[0]),  item[1], item[2], item[3],item[4],item[5],item[6],item[7],item[8]])
    for item in rp:
        outputWriter.writerow(["N/A",item[0], item[1],item[2],item[3],item[4]])


#if __name__ == '__main__':
def main(email, passwordy, theFileToBeScanned, program_emails):
    global any_errors
    any_errors = {'errors':[]}
    try:
        df = pd.read_table(theFileToBeScanned)
    except Exception as e:
        any_errors['errors'].append("ResComplyXLS.xls file could not be found")
    #try:
    #    df = pd.read_excel('ResComply.xlsx')
    #except FileNotFoundError:
    #    any_errors['errors'].append("ResComply.xlsx file could not be found")
    #    return any_errors

    df=df.fillna({'Start Time':"01:01 AM",'End Time':"01:01 AM",'Duration (Minutes)':1,"FormBuilder Form Included":"MISSING","Service Type":"Not applicable"})
    df.index = df.index + 2

    scan_data_before_cleaning = [df.columns.tolist()] + df.reset_index().values.tolist()
    del scan_data_before_cleaning[0]
    removals = []
    for item in scan_data_before_cleaning:
        try:
            item[3] = dt.datetime.strptime(item[3], "%m/%d/%Y")
        except:
            pass # If we can't conver it to a date, then it means there is data in there
        try:
            item[5] = dt.datetime.strptime(item[5], "%I:%M %p").time()
        except:
            pass
        try:
            item[6] = dt.datetime.strptime(item[6], "%I:%M %p").time()
        except:
            pass

    scan_data = [item for item in scan_data_before_cleaning if item not in removals]
    results_list, reports_list=[],[]

    global nameProgramRes
    nameProgramRes = {}
    for item in scan_data:
        if item[9] == "Residential Group Home":
            nameProgramRes[item[2]] = item[4]


    noteLength(scan_data,results_list)
    duplicate_notes(scan_data, reports_list)
    duplicate_content(scan_data,results_list)
    name_checker(scan_data, results_list)
    #timeModified(scan_data, reports_list)
    noteType(scan_data, results_list)
    svcType(scan_data, results_list)
    eSigned(scan_data,results_list)
    missingForm(scan_data, results_list)
    record_count(scan_data, reports_list,3)

    myDict = {}
    #new_results_list = sorted(results_list,key=lambda x: x[0]) #Slowing everything down?? Not tested a/o 12-20-18
    for item in results_list:
        if not item[0] in myDict:
            myDict[item[0]] = [[], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]]
        myDict[item[0]][0].append(item[1])

    current_path = Path.cwd()
    yr = str(dt.datetime.now().date().year)
    sub = current_path/"Montly-QA-Results"/yr
    if not sub.is_dir():
        Path(sub).mkdir(parents=True, exist_ok=True)
    todays_date_file = str(dt.datetime.now().date()) + '.csv'
    outputfile = Path(sub/todays_date_file)
    outputfile.touch()
    with outputfile.open('w',newline='') as f:
        outputWriter = csv.writer(f)
        outputWriter.writerow(['Row#','Flagged Word/Phrase', 'Individual', 'Date', 'Program', 'Excerpt', 'Start Time', 'End Time', 'Duration','Staff', 'Audit Comments'])
        csvWritee(myDict, reports_list, outputWriter) # Write all results to the outputFile
    pd.set_option('display.max_colwidth', None)
    dfNew = pd.read_csv(outputfile)
    dfNew = dfNew.drop(columns=['Row#', 'Audit Comments'])
    errors_and_warnings = {'errors':[],'warnings':[]}
    sendEmailSuccess = sendEmail(dfNew, email, passwordy, errors_and_warnings, program_emails)

    return sendEmailSuccess
