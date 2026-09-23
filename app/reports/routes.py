from datetime import datetime, timedelta
from io import BytesIO

from flask import render_template, request, send_file
from xhtml2pdf import pisa

from app.models import AccessLog
from app.reports import reports


@reports.route('/report/pdf')
def report_pdf():
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    query = AccessLog.query

    if start_date:
        query = query.filter(AccessLog.entry_time >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(AccessLog.entry_time < end)

    logs = query.order_by(AccessLog.entry_time.desc()).all()
    html = render_template(
        'reports/pdf_lite.html', logs=logs, now=datetime.now(),
        start_date=start_date, end_date=end_date
    )
    output = BytesIO()
    result = pisa.pisaDocument(BytesIO(html.encode('utf-8')), dest=output)
    if result.err:
        return 'Não foi possível gerar o PDF.', 500

    output.seek(0)
    filename = f'relatorio_acessos_{datetime.now():%Y%m%d_%H%M}.pdf'
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/pdf')
