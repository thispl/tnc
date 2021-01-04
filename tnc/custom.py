import frappe,os
import random
from datetime import datetime
from frappe.utils.data import today, add_days
from dateutil.relativedelta import relativedelta
from datetime import timedelta


@frappe.whitelist()
def generate_qr(employee):
    can = frappe.get_doc("Employee",employee)
    import qrcode
    import qrcode.image.pil
    from PIL import Image



    # Create qr code instance
    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size = 4,
        border = 4,
    )
   
    # The data that you want to store
    data = """Employee Name:%s\nImage:%s\nCategory:%s\nUAN:%s\nESI IP No:%s\nSubContractor ID:%s\nSubContractor Name:%s\nGender:%s\nDate of Birth:%s\nBlood Group:%s"""%(can.employee_name,can.image,can.category,can.uan,can.esi_ip_no,can.subcontractor_id,can.
subcontractor_name,can.gender,can.date_of_birth,can.blood_group)
    # Add data
    qr.add_data(data)
    qr.make(fit=True)
    # Create an image from the QR Code instance
    img = qr.make_image()
    path = frappe.get_site_path('public', 'files')
    qr_name = can.employee_name + '_qr.png'
    # basewidth = 64
    # wpercent = (basewidth / float(img.size[0]))
    # hsize = int((float(img.size[1]) * float(wpercent)))
    # img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    img.save(path +"/%s"% qr_name)
    frappe.errprint(can.name)
    frappe.db.set_value("Employee",can.name,"qr_code","/files/%s"%qr_name)
    return qr_name

@frappe.whitelist()
def check_gross_against_ss(doc,method):
    from erpnext.payroll.doctype.salary_structure.salary_structure import make_salary_slip
    ss = make_salary_slip(doc.salary_structure,employee = doc.employee)
    frappe.errprint(ss.gross_pay)
    frappe.errprint(doc.base)


@frappe.whitelist()
def get_check():
    checkins = frappe.db.sql(
        """select * from `tabEmployee Checkin` where attendance_marked = 0 """, as_dict=1)
    if checkins:
        for c in checkins:
            # print("hi")
            # print(c)
            # print(c.employee,c.device_area,c.log_date, c.biometric_pin,c.log_type,c.time)
            att = mark_attendance_from_checkin(c.employee,c.device_area,c.log_date,
                             c.biometric_pin,c.log_type,c.time)

            if att:
                frappe.db.set_value("Employee Checkin",
                                    c.name, "attendance_marked", "1")
        return "ok"

def mark_attendance_from_checkin(employee,device_area,log_date,biometric_pin,log_type,time):
    # print(employee,device_area,log_date,biometric_pin,log_type,time)
    a_min_time = datetime.strptime('05:00', '%H:%M')
    a_max_time = datetime.strptime('08:00', '%H:%M')
    b_min_time = datetime.strptime('12:00', '%H:%M')
    b_max_time = datetime.strptime('20:00', '%H:%M')
    c_min_time = datetime.strptime('20:00', '%H:%M')
    c_max_time = datetime.strptime('05:00', '%H:%M')
    c_max_time1 = datetime.strptime('06:30', '%H:%M')
    g_min_time = datetime.strptime('08:00', '%H:%M')
    g_max_time = datetime.strptime('12:00', '%H:%M')
    ot_from_time =datetime.strptime('08:00','%H:%M')
    employee = frappe.db.get_value("Employee", {
        "biometric_pin": biometric_pin, "status": "Active"})
    if employee:
        date = log_date
        time_m = time
        emp = frappe.get_doc("Employee", employee)
        c_time = datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S').time()
        att_time = datetime.strptime(str(c_time), '%H:%M:%S')
        # print(att_time)
        if(log_type=="IN"):
            # print("IN")
            if att_time >= a_min_time and att_time <= a_max_time:
                shift = "A"
                status = "Present"
            elif att_time >= b_min_time and att_time <= b_max_time:
                shift = "B"
                status = "Present"
            elif att_time >= c_min_time and att_time <= c_max_time:
                shift = "C"
                status = "Present"
            elif att_time >= g_min_time and att_time <= g_max_time:
                shift ="G"
                status ="Present"    
            else:
                status = "Absent"
            # print (shift)
            # print(att_time)
            attendance = frappe.new_doc("Attendance")
            attendance.update({
                "employee": emp.employee,
                "status": status,
                "attendance_date":log_date,
                "intime": att_time,
                "outtime":"",
                "shift": shift
            })
            attendance.save(ignore_permissions=True)
            frappe.errprint(attendance)
            attendance.submit()
            frappe.db.commit()
            frappe.response.type = "text"
            return "ok"
        elif(log_type=="OUT"):
            if att_time <= c_max_time1:
                # print(log_date,att_time)
                if frappe.db.exists("Attendance",{"attendance_date":add_days(log_date,-1),"employee":emp.name}):
                    attendance=frappe.get_doc("Attendance",{"attendance_date":add_days(log_date,-1),"employee":emp.name})
                    out_date = log_date
                    print(att_time)
                    print(attendance.name)
                    # frappe.db.set_value("Attendance",attendance.name,"out",att_time)
                
                attendance.update({
                    "outtime": att_time,
                    "out_date":out_date
                })
                attendance.save(ignore_permissions=True)
                    # attendance.submit()
                frappe.db.commit()
                frappe.response.type = "text"
                return "ok"
            else:
                if frappe.db.exists("Attendance",{"attendance_date":log_date,"employee":emp.name}):
                    # print(log_date,att_time)
                    attendance=frappe.get_doc("Attendance",{"attendance_date":log_date,"employee":emp.name})
                    # frappe.db.set_value("Attendance",attendance.name,"out",att_time)
                    out_date = log_date
                    inti = datetime.strptime(str(attendance.intime), '%H:%M:%S')
                    print(inti)
                    at_time = datetime.strftime(att_time, '%Y-%m-%d %H:%M:%S')
                    a_time = datetime.strptime(str(at_time), '%Y-%m-%d %H:%M:%S').time()
                    att_time = datetime.strptime(str(a_time), '%H:%M:%S')
                    # att = datetime.strptime(str(att_time), '%H:%M:%S')
                    print(att_time)
                    twh={}
                    twh=(att_time-inti)
                    
                    print(twh)
                    twh = datetime.strptime(str(twh), "%H:%M:%S")
                    t =twh.strftime("%H")
                    t1=int(t)
                    print(t1)
                    if t1 >= 4 and t1 < 9:
                        status = "Present"
                        # print(status)
                    elif t1 >= 9:
                        status = "Present"
                        print(status)
                        # date=log_date
                        # at_time = datetime.strftime(da, '%Y-%m-%d %H:%M:%S')
                        # date= datetime.strptime(str(at_time), '%Y-%m-%d %H:%M:%S')
                        # print(date)
                        # print(type(date))
                        
                        from_time = attendance.intime + ot_from_time
                        f_time = from_time.time()
                        print(type(f_time))
                        from_time = datetime.combine( date,f_time)
                        print(from_time)
                        print(type(from_time))
                        a_time=att_time.time()
                        at_time =datetime.combine(date,a_time)
                        hrs=at_time-from_time
                        # time_d_ms  = hrs/ datetime.timedelta(milliseconds=1)
                        time_d_float = hrs.total_seconds()
                        hour = time_d_float // 3600
                        print(hour)
                        print(attendance.shift)     
                        ts=frappe.db.sql("""select name from `tabEmployee` where ot_applicable = 1 """, as_dict=1)
                        if ts:
                            timesheet=frappe.new_doc("Timesheet") 
                            print(emp.name)
                            # print(log_date)
                            print(type(hrs))
                            timesheet.employee=emp.name
                            timesheet.append("time_logs",{ 
                                "activity_type":"Over Time",
                                "from_time":from_time,
                                "to_time":at_time,
                                "hours":hour
                            })
                            timesheet.save(ignore_permissions=True)
                            frappe.db.commit()
                            
                    else:
                        status = "Absent"
                    attendance.update({
                        "outtime": att_time,
                        "out_date":out_date,
                        # "status": status
                    })
                    # print(attendance.outtime)
                    attendance.save(ignore_permissions=True)
                    # attendance.submit()
                    frappe.db.commit()
                    frappe.response.type = "text"
                    return "ok"
# def total_working_hours():
#     twh = frappe.db.sql(
#         """select abs(timestampdiff(hour, s.in, s.out)),s.out,s.in  from `tabAttendance` s """, as_dict=1)   
#     print(twh) 
#     if twh >= 4 and twh <= 9:
#         status = "Present"
#     elif twh >= 9:
#         status = "Present"
#         frappe.new_doc("Timesheet")    
#     else:
#         status = "Absent"
#     attendance.update({
#          "status": status
#         })    
#     return status
