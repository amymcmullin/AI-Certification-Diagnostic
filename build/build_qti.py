"""Build a Canvas-compatible QTI 1.2 quiz package from a question pack.

Canvas: Course Settings > Import Course Content > QTI .zip file.
Questions are ordered by topic; Canvas shuffles answer choices.
The package contains the answer key, so a private pack's package must stay private.
"""
import html, zipfile


def build_qti(b, out):
    E=lambda s: html.escape(s, quote=True)
    QID="g_"+b["settings"]["id"]+"_diagnostic"
    order=list(b["topics"].keys())
    title=b["settings"].get("title","Certification Diagnostic")
    items=[]
    for t in order:
        items+= [i for i in b['items'] if i['topic']==t]
    def item_xml(n,it):
        multi=it['type']=='ma'
        qtype='multiple_answers_question' if multi else 'multiple_choice_question'
        ids=[f"{it['id']}_{k}" for k in range(len(it['options']))]
        stem=it['stem']
        resp="".join(f'<response_label ident="{ids[k]}"><material><mattext texttype="text/plain">{E(o)}</mattext></material></response_label>' for k,o in enumerate(it['options']))
        card='Multiple' if multi else 'Single'
        if multi:
            conds="".join(f'<varequal respident="response1">{ids[k]}</varequal>' if k in it['answer'] else f'<not><varequal respident="response1">{ids[k]}</varequal></not>' for k in range(len(ids)))
            proc=f'<respcondition continue="No"><conditionvar><and>{conds}</and></conditionvar><setvar varname="SCORE" action="Set">100</setvar></respcondition>'
        else:
            proc=f'<respcondition continue="No"><conditionvar><varequal respident="response1">{ids[it["answer"][0]]}</varequal></conditionvar><setvar varname="SCORE" action="Set">100</setvar></respcondition>'
        topic=b['topics'][it['topic']]['name']
        return f'''<item ident="{it['id']}" title="Q{n:02d} {E(topic)}">
    <itemmetadata><qtimetadata>
    <qtimetadatafield><fieldlabel>question_type</fieldlabel><fieldentry>{qtype}</fieldentry></qtimetadatafield>
    <qtimetadatafield><fieldlabel>points_possible</fieldlabel><fieldentry>1.0</fieldentry></qtimetadatafield>
    <qtimetadatafield><fieldlabel>original_answer_ids</fieldlabel><fieldentry>{",".join(ids)}</fieldentry></qtimetadatafield>
    <qtimetadatafield><fieldlabel>assessment_question_identifierref</fieldlabel><fieldentry>aq_{it['id']}</fieldentry></qtimetadatafield>
    </qtimetadata></itemmetadata>
    <presentation><material><mattext texttype="text/html">{E("<p>"+E(stem)+"</p>")}</mattext></material>
    <response_lid ident="response1" rcardinality="{card}"><render_choice>{resp}</render_choice></response_lid></presentation>
    <resprocessing><outcomes><decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/></outcomes>{proc}</resprocessing>
    <itemfeedback ident="general_fb"><flow_mat><material><mattext texttype="text/html">{E("<p>"+E(it['why'])+"</p>")}</mattext></material></flow_mat></itemfeedback>
    </item>'''
    body="\n".join(item_xml(n+1,it) for n,it in enumerate(items))
    assess=f'''<?xml version="1.0" encoding="UTF-8"?>
    <questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd">
    <assessment ident="{QID}" title="{E(title)}">
    <qtimetadata><qtimetadatafield><fieldlabel>cc_maxattempts</fieldlabel><fieldentry>1</fieldentry></qtimetadatafield></qtimetadata>
    <section ident="root_section">
    {body}
    </section></assessment></questestinterop>'''
    exams=", ".join(e["name"] for e in b["exams"].values())
    desc=E(f"<p>{len(b['items'])} questions covering {exams}. Answer every question; “Choose two” items need both answers right.</p>")
    meta=f'''<?xml version="1.0" encoding="UTF-8"?>
    <quiz identifier="{QID}" xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
    <title>{E(title)}</title><description>{desc}</description>
    <shuffle_answers>true</shuffle_answers><scoring_policy>keep_highest</scoring_policy><quiz_type>assignment</quiz_type>
    <points_possible>{float(len(b["items"]))}</points_possible><show_correct_answers>false</show_correct_answers><allowed_attempts>1</allowed_attempts>
    <one_question_at_a_time>false</one_question_at_a_time><time_limit>{int(b["settings"].get("minutes",40))+5}</time_limit><anonymous_submissions>false</anonymous_submissions>
    <available>false</available><assignment_group_identifierref></assignment_group_identifierref>
    </quiz>'''
    manifest=f'''<?xml version="1.0" encoding="UTF-8"?>
    <manifest identifier="m_{QID}" xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1" xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd">
    <metadata><schema>IMS Content</schema><schemaversion>1.1.3</schemaversion></metadata>
    <organizations/>
    <resources>
    <resource identifier="{QID}" type="imsqti_xmlv1p2"><file href="{QID}/{QID}.xml"/><dependency identifierref="r_meta"/></resource>
    <resource identifier="r_meta" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" href="{QID}/assessment_meta.xml"><file href="{QID}/assessment_meta.xml"/></resource>
    </resources></manifest>'''
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('imsmanifest.xml',manifest)
        z.writestr(f'{QID}/{QID}.xml',assess)
        z.writestr(f'{QID}/assessment_meta.xml',meta)
    return len(items)

