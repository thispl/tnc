import frappe,os
import random


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
