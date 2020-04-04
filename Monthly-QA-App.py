import PySimpleGUI as sg
import ResCompliance

sg.theme('BluePurple')
with open('emails.txt', 'r') as f:
    myText = f.readlines()


def updateEmails(v):
    with open('emails.txt', 'w') as f:
        f.write(v)

def check_emails(vals):
    # Tidy up the list of emails and program names
    res = vals.splitlines()
    for x in res:
        x = x.strip().rstrip().replace("[", "").replace("'", "")
    res = [i for i in res if i]
    program_emails = {}
    for item in res:
        v = item.split(",")
        try:
            program_emails[v[0].lower()] = [v[1], v[2]]
        except:
            return False
    return program_emails
layout = [[sg.Text(''), sg.Text(size=(30,1), key='-OUTPUT-')],
            [sg.Text("Enter email"), sg.Input(key='email')],
          [sg.Text("Enter password"), sg.Input(key='password', password_char="*")],
           [sg.Text('Choose file (xlsx or xls)', size=(8, 1)), sg.Input(), sg.FileBrowse()],
           [sg.Text('Program Name,Email-1,Email-2 (sep by comma)'), sg.Text(size=(30,1))],
           [sg.Multiline(''.join(myText), size=(70, 9))],
          [sg.Button('Run!'), sg.Button('Exit')]]

window = sg.Window('Monthly QA Scans', layout,finalize=True,size=(625,325))

while True:  # Event Loop
    event, values = window.read()
    if event in  (None, 'Exit'):
        break
    if event == 'Run!' and values['email'] == '' or values['password'] == '':
        window['-OUTPUT-'].update('Email and password are required!')
        window['-OUTPUT-'].update(text_color='red')
        continue
    if len(values[0]) == 0: # values[0] is the string of the file.  If 0 they didn't choose a file
        window['-OUTPUT-'].update('Please choose a file to scan!')
        window['-OUTPUT-'].update(text_color='red')
        continue
    checky = check_emails(values[1])
    if event == 'Run!' and not checky:
        window['-OUTPUT-'].update('Two emails per program, please!')
        window['-OUTPUT-'].update(text_color='red')
        continue

    updateEmails(values[1])
    anyErrors = ResCompliance.main(values['email'], values['password'], values[0], checky)
    if len(anyErrors['errors'])> 0:
        sg.popup(''.join(anyErrors['errors']), text_color='red')
        continue
    if len(anyErrors['warnings']) > 0:
        sg.popup('Success, but the following emails could not be found \
                for the following program(s): '+'; '.join(anyErrors['warnings']), text_color='red')
        break
    else:
        sg.popup("Success!")
        break

window.close()
