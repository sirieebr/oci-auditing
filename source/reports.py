import os,re
from datetime import datetime
from time import gmtime, strftime, sleep

def init(a):
	global ui,the,conf
	the=a
	ui=the.ui
	conf=the.conf

def generateReport():
	import xlsxwriter
	end_time_local = datetime.now().strftime('%Y-%m-%d %H:%M:%S'); time_zone = strftime("[%z]", gmtime())
	end_time_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
	ui.setInfo('Generating final Excel Report ...')
	global workbook,ws,row,format,startRow,data,head,cols,service
	auditIssuesFound=False
	reportName = the.startTime + ' OCI Auditing Report.xlsx'
	reportDirPath = conf.resDr
	reportPath = reportDirPath + '\\' + reportName
	workbook = xlsxwriter.Workbook(reportPath)
	
	workbook.set_properties({
		'title'   : 'OCI Auditing Report',
		'subject' : 'Reports of Oracle Cloud Infrastructure tenancy components',
		'author'  : 'Karthik Kumar HP',
		'manager' : 'Karthik.Hiraskar@oracle.com',
		'company' : 'Oracle',
		'category': 'Reports',
		'keywords': 'OCI, Report, Audit',
		'comments': 'Created by '+the.tool_name+', ver '+the.version,
		'status'  : ' ',
	})
	
	format = addAllFormatsToWorkbook()
	
	addTab('Tenancies', colWidths=[14,50,40,65])
	
	ws.write_rich_string('B1', format['bold'], end_time_local, format['normal'], '  ', time_zone)
	ws.write_rich_string('C1', format['bold'], end_time_utc, format['normal'], '  [UTC]')
	
	row=2
	ws.write(row,2, '** first one is home-region', format['normal_small'])
	row+=1
	writeHeader('Tenancy','Tenancy OCID','Subscribed Regions','Availability Domains')
	ws.freeze_panes(row,0)
	sortedTenancies = sorted(the.tenancies.keys())
	
	for t in sortedTenancies:
		regions = the.tenancies[t][1]
		rowHeight = 8.5 * len(regions)
		if rowHeight>15: ws.set_row(row, rowHeight) # 15 is normal height
		avlDomains=[]
		for rgn in regions:
			avlDomains.append(', '.join(the.tenancies[t][2][rgn]))
		ws.write(row,0, t, format['tblCell'])
		ws.write(row,1, the.tenancies[t][0], format['tblCell_f6_wrap'])
		if len(regions)>0:
			homeRegion = regions.pop(0) # home-region taken out from regions list 
			otherSubscribedRegions = ', -'
			if len(regions)>0: otherSubscribedRegions = ', ' + ', '.join(regions)
			ws.write_rich_string(row,2, format['italic_underlined'], homeRegion, format['normal'], otherSubscribedRegions, format['tblCell_wrap'])
		else:
			ws.write_rich_string(row,2, format['italic'], '-- Not Able to get Regions', format['normal'], ' !', format['tblCell'])
			
		ws.write(row,3, '\n'.join(avlDomains), format['tblCell_f6_wrap'])
		row+=1
	ws.autofilter(startRow, 0, row-1, 3)
	row+=2
	if len(the.issueTenancies)>0:
		ws.write(row,1, 'Tenancies failed to connect:',format['bold_underlined'])
		row+=1
		for t in the.issueTenancies:
			ws.write(row,1, t, format['italic'])
			row+=1
	row+=2; ws.write_rich_string(row, 1, '-- This Report is Created by: ', format['bold'], the.tool_name, format['normal'], ', Version ', format['bold'], the.version, format['normal'])
	row+=1; ws.write(row, 1, 'Log File: ' + conf.logfile, format['normal_small'])
	row+=2; ws.set_selection(row, 0, row, 0)
	# print('KK - Tenancies Over')
	
	def addCountSummary(row, dict):
		ws.write(row,0, 'Count Summary:',format['bold_underlined'])
		row+=1
		for t in sortedTenancies:
			ws.write(row,0, t, format['italic'])
			ws.write(row,1, len(dict[t]), format['italic_left'])
			row+=1
		ws.set_selection(row+1, 2, row+1, 2)
	
	if ui.parentWindow.m_checkBox_Users.GetValue():
		addTab('Users', colWidths=[14,30,30,30,65,20,30])
		writeHeader('Tenancy','User Name','Description','Email','OCID','Created','Report Comments')
		ws.freeze_panes(row,0)
		
		for t in sortedTenancies:
			for k in sorted(the.users[t].keys()):
				# Date Time pattern update, Ex: 2019-08-01T06:33:51.715+0000 => 2019-08-01 06:33:51
				creatDate=the.dateFormat(the.users[t][k][4])
				cmnt=the.users[t][k][5]
				cl_format = format['tblCell']
				cl_format_small = format['tblCell_f8']
				if cmnt:
					cl_format = format['tblCell_hig']
					cl_format_small = format['tblCell_hig_f8']
				ws.write(row,0, t, cl_format)
				ws.write(row,1, the.users[t][k][0], cl_format)
				ws.write(row,2, the.users[t][k][1], cl_format)
				ws.write(row,3, the.users[t][k][2], cl_format)
				ws.write(row,4, the.users[t][k][3], cl_format_small)
				ws.write(row,5, creatDate,      cl_format)
				ws.write(row,6, cmnt,           cl_format_small)
				row+=1
		ws.autofilter(0, 0, row-1, 6)
		addCountSummary(row+2, the.users)
	
	if ui.parentWindow.m_checkBox_Groups.GetValue():
		addTab('Groups', colWidths=[14,30,30,65,20,30])
		writeHeader('Tenancy','Group Name','Description','OCID','Created','Report Comments')
		ws.freeze_panes(row,0)
		
		for t in sortedTenancies:
			for k in sorted(the.groups[t].keys()):
				creationDate=the.dateFormat(the.groups[t][k][3])
				cmnt=the.groups[t][k][4]
				cl_format = format['tblCell']
				cl_format_small = format['tblCell_f8']
				if cmnt:
					cl_format = format['tblCell_hig']
					cl_format_small = format['tblCell_hig_f8']
				ws.write(row,0, t, cl_format)
				ws.write(row,1, the.groups[t][k][0], cl_format)
				ws.write(row,2, the.groups[t][k][1], cl_format)
				ws.write(row,3, the.groups[t][k][2], cl_format_small)
				ws.write(row,4, creationDate, cl_format)
				ws.write(row,5, cmnt, cl_format_small)
				row+=1
		ws.autofilter(0, 0, row-1, 5)
		addCountSummary(row+2, the.groups)
	
	if ui.parentWindow.m_checkBox_Compartments.GetValue():
		addTab('Compartments', colWidths=[14,30,65,7,9,35,35])
		writeHeader('Tenancy','Compartment Name','Compartment OCID','Level','Status','Compartment Description','Report Comments')
		ws.freeze_panes(row,0)
		
		for t in sortedTenancies:
			for k in sorted(the.compartments[t].keys()):
				cl_format = format['tblCell']
				cl_format_small = format['tblCell_f8']
				if the.compartments[t][k][5]:
					cl_format = format['tblCell_hig']
					cl_format_small = format['tblCell_hig_f8']
				ws.write(row,0, t, cl_format)
				ws.write(row,1, the.compartments[t][k][0], cl_format)
				ws.write(row,2, the.compartments[t][k][1], cl_format_small)
				ws.write(row,3, the.compartments[t][k][2], cl_format)
				ws.write(row,4, the.compartments[t][k][3], cl_format)
				ws.write(row,5, the.compartments[t][k][4], cl_format)
				ws.write(row,6, the.compartments[t][k][5], cl_format_small)
				row+=1
		ws.autofilter(0, 0, row-1, 6)
		addCountSummary(row+2, the.compartments)
	# print('KK - Compartments Over')
	
	if ui.parentWindow.m_checkBox_serviceLimits.GetValue():
		addTab('Service Limits', colWidths=[14,22,22,25,30,18,18,18])
		if conf.limitsShowUsed:
			writeHeader('Tenancy','Service','Scope','Limit Name','Limit Description','Service Limit','Service Used','Service Available')
		else:
			writeHeader('Tenancy','Service','Scope','Limit Name','Limit Description','Service Limit')
		ws.freeze_panes(row,0)
		
		for t in sortedTenancies:
			for k in sorted(the.limits[t].keys()):
				cl_format = format['tblCell']
				lmt = the.limits[t][k][4]
				if conf.limitsShowUsed:
					usd = the.limits[t][k][5]
					avl = the.limits[t][k][6]
					if usd!=0 and conf.validate['LIMITS']:
						if   usd>lmt : cl_format=format['tblCell_hig']
						elif usd>(lmt*conf.limits_alert_value): cl_format=format['tblCell_med']
				ws.write(row,0, t, cl_format)
				ws.write(row,1, the.limits[t][k][0], cl_format)
				ws.write(row,2, the.limits[t][k][1], cl_format)
				ws.write(row,3, the.limits[t][k][2], cl_format)
				ws.write(row,4, the.limits[t][k][3], cl_format)
				ws.write(row,5, lmt, cl_format)
				if conf.limitsShowUsed:
					ws.write(row,6, usd, cl_format)
					ws.write(row,7, avl, cl_format)
				row+=1
		if conf.limitsShowUsed: ws.autofilter(0, 0, row-1, 7)
		else: ws.autofilter(0, 0, row-1, 5)
		
		if len(conf.limitsSkipServices)>0:
			row+=3
			ws.write(row,0, 'Skipped Services:', format['bold_underlined'])
			row+=1
			colStart=0; colEnd=7
			col=colStart
			for srv in conf.limitsSkipServices:
				ws.write(row,col, srv, format['italic'])
				if col<colEnd:
					col+=1
				else:
					row+=1 # Next row & reinitiate col
					col=colStart
		# addCountSummary(row+2, the.limits)
	
	if ui.parentWindow.m_checkBox_Policies.GetValue():
		addTab('Policies', colWidths=[14,30,30,70,35])
		writeHeader('Tenancy','Compartment','Policy Name','Policy Statement','Report Comments')
		ws.freeze_panes(row,0)
		
		for t in sortedTenancies:
			for k in sorted(the.policies[t].keys()):
				cl_format = format['tblCell']
				cl_format_small = format['tblCell_f8']
				if the.policies[t][k][3]:
					cl_format = format['tblCell_hig']
					cl_format_small = format['tblCell_hig_f8']
				ws.write(row,0, t, cl_format)
				ws.write(row,1, the.policies[t][k][0], cl_format)
				ws.write(row,2, the.policies[t][k][1], cl_format)
				ws.write(row,3, the.policies[t][k][2], cl_format_small)
				ws.write(row,4, the.policies[t][k][3], cl_format_small)
				row+=1
		ws.autofilter(0, 0, row-1, 4)
		addCountSummary(row+2, the.policies)
		
	if ui.parentWindow.m_checkBox_Instances.GetValue():
		addTab('Services Created', colWidths=[14,25,35,35,35,35,20])
		ws.write(row,4,'* Extra Fields information at the end',format['normal_small'])
		row+=1
		writeHeader('Tenancy','Compartment','Cloud Service','Display Name','Field-1','Field-2','Created')
		ws.freeze_panes(row,0)
		
		for t in sortedTenancies:
			for k in sorted(the.instances[t].keys()):
				ws.write(row,0, t, format['tblCell'])
				ws.write(row,1, the.instances[t][k][0], format['tblCell'])
				ws.write(row,2, the.instances[t][k][1], format['tblCell'])
				ws.write(row,3, the.instances[t][k][2], format['tblCell'])
				ws.write(row,4, the.instances[t][k][3], format['tblCell'])
				ws.write(row,5, the.instances[t][k][4], format['tblCell'])
				ws.write(row,6, the.instances[t][k][5], format['tblCell'])
				row+=1
		ws.autofilter(1, 0, row-1, 6)
		
		row+=1
		ws.write(row,1, 'Extra Fields Information:', format['bold_underlined'])
		selectedServices = ui.getUIselection('audits', 'ociServices') # array of selected services
		for srv in selectedServices:
			row+=1
			ws.write(row,2, srv, format['italic_downBorder'])
			ws.write(row,3, '',   format['italic_downBorder'])
			ws.write(row,4, the.ociServices[srv]['xtraFieldsInfo'][0], format['italic_downBorder'])
			ws.write(row,5, the.ociServices[srv]['xtraFieldsInfo'][1], format['italic_downBorder'])
		
		if len(conf.disableCompartments)>0:
			row+=2
			ws.write(row,1, 'Disabled Compartments List:', format['bold_underlined'])
			row+=1
			colStart=1; colEnd=5
			col=colStart
			for comp in conf.disableCompartments:
				ws.write(row,col, comp, format['italic'])
				if col<colEnd:
					col+=1
				else:
					row+=1 # Next row & reinitiate col
					col=colStart
		addCountSummary(row+2, the.instances)
	
	if ui.parentWindow.m_checkBox_Events.GetValue():
		addTab('Events', colWidths=[14,20,15,40,30,30,30,19])
		writeHeader('Tenancy','Compartment','Region','User','Event Source','Event Name','Resource Name','Event Time')
		ws.freeze_panes(row,0)
		
		showAll=False
		if 'events_show_all' in conf.keys: showAll=True
		cl_format = format['tblCell']
		cl_format_small = format['tblCell_f8']
		for t in sortedTenancies:
			for k in sorted(the.events[t].keys()):
				evt=the.events[t][k]
				event_source = evt[4]
				event_name = evt[5]
				if evt[0] or showAll:
					if evt[0]: auditIssuesFound=True
					writeRow(data=[t,evt[1],evt[2],evt[3],event_source,event_name,evt[6],evt[7]], style=getStyle(risk=evt[0]))
		ws.autofilter(0, 0, row-1, 7)
		row+=2; ws.write(row,0, 'Audit Events, selected start & end dates:',format['bold_underlined'])
		row+=1
		ws.write(row,0, str(the.eventDates['start']), format['italic'])
		ws.write(row,2, str(the.eventDates['end']), format['italic'])
		addCountSummary(row+2, the.events)
	
	if ui.parentWindow.m_checkBox_Networking.GetValue():
		addTab('VCN', colWidths=[20,20,20,20,20,15,18], tabColor='#632523')
		addHeading2('VCN')
		writeHeader('Tenancy','Region','Compartment','Name','OCID','CIDR Block','Created Time')
		## VCN
		for t in sorted(the.networks['VCN'].keys()):
			for r in sorted(the.networks['VCN'][t].keys()):
				for c in sorted(the.networks['VCN'][t][r].keys()):
					for n in sorted(the.networks['VCN'][t][r][c].keys()):
						v=the.networks['VCN'][t][r][c][n]
						writeRow(data=[t,r,c,n,v[0],v[1],v[2]], style=getStyle(f6=[4]))
		finalTouchTable()
		
		if len(conf.disableCompartments)>0:
			row+=3
			ws.write(row,0, 'Disabled Compartments List:', format['bold_underlined'])
			row+=1
			colStart=0; colEnd=7
			col=colStart
			for comp in conf.disableCompartments:
				ws.write(row,col, comp, format['italic'])
				if col<colEnd:
					col+=1
				else:
					row+=1 # Next row & reinitiate col
					col=colStart
		
		nwSerSel=ui.getUIselection('audits', 'networkComponents')
		
		service='Route Table'
		if service in nwSerSel:
			addTab('RT', colWidths=[20,20,20,20,20,20], tabColor='#632523')
			addHeading2(service+'s')
			generateHeaderList('VCN OCID','RT Name','RT OCID','Created Time')
			for vcnID in the.networks[service].keys():
				for rt in the.networks[service][vcnID]: data.append([vcnID, rt[0], rt[1], rt[2]])
			addTable()
				
			service='route_rules'
			row+=1
			addHeading2('Route Rules', hx='h3')
			writeHeader('RT OCID','Destination','Destination Type','Network Entity OCID','Description')
			for rtID in the.networks[service].keys():
				for rr in the.networks[service][rtID]:
					writeRow(data=[rtID, rr[0], rr[1], rr[2], rr[3]], style=['tblCell_f6','tblCell','tblCell','tblCell_f6','tblCell'])
			finalTouchTable()
		
		service='Subnet'
		if service in nwSerSel:
			addTab(service+'s', colWidths=[20,30,20,15,18,20,18], tabColor='#632523')
			addHeading2(service+'s')
			generateHeaderList('VCN OCID','Name','OCID','CIDR','Access','Security List OCIDs','Created Time')
			for vcnID in the.networks[service].keys():
				for sn in the.networks[service][vcnID]: data.append([vcnID, sn[0], sn[1], sn[2], sn[3], sn[4], sn[5]])
			addTable()
				
		service='Security List'
		if service in nwSerSel:
			addTab('SL', colWidths=[20,30,20,20,20,12,20,20,20], tabColor='#632523')
			addHeading2(service+'s')
			generateHeaderList('VCN OCID','SL Name','SL OCID','Created Time')
			for vcnID in the.networks[service].keys():
				for sl in the.networks[service][vcnID]: data.append([vcnID, sl[0], sl[1], sl[2]])
			addTable()
				
			service='sl_egress_security_rules'
			row+=1
			ws.merge_range(row,0,row,3,'SL - Security Rules',format['h3'])
			ws.write(row,6,'type / source_port_range',format['normal_small'])
			ws.write(row,7,'code / destination_port_range',format['normal_small'])
			row+=1
			writeHeader('SL OCID','Egress/Ingress Rule','Stateless','Destination/Source Type','Destination/Source','Protocol','Field-1','Field-2','Description')
			for slID in the.networks[service].keys():
				for egr in the.networks[service][slID]:
					if egr[0]: auditIssuesFound=True
					writeRow(data=[slID, 'Egress', egr[1], egr[2], egr[3], egr[4], egr[5], egr[6], egr[7]], style=getStyle(risk=egr[0], f6=[0]))
			service='sl_ingress_security_rules'
			for slID in the.networks[service].keys():
				for ing in the.networks[service][slID]:
					if ing[0]: auditIssuesFound=True
					writeRow(data=[slID, 'Ingress', ing[1], ing[2], ing[3], ing[4], ing[5], ing[6], ing[7]], style=getStyle(risk=ing[0], f6=[0]))
			finalTouchTable()
				
		service='Network Security Group'
		if service in nwSerSel:
			addTab('NSG', colWidths=[20,20,20,20,20,12,20,20,20,18], tabColor='#632523')
			addHeading2(service+'s')
			generateHeaderList('VCN OCID','NSG Name','NSG OCID','Created Time')
			for vcnID in the.networks[service].keys():
				for nsg in the.networks[service][vcnID]: data.append([vcnID, nsg[0], nsg[1], nsg[2]])
			addTable()
				
			service='nsg_security_rules'
			row+=1
			ws.merge_range(row,0,row,3,'NSG - Security Rules',format['h3'])
			ws.write(row,7,'type / source_port_range',format['normal_small'])
			ws.write(row,8,'code / destination_port_range',format['normal_small'])
			row+=1
			writeHeader('NSG OCID','Stateless','Direction','Type Source/Destination','Source/Destination','Protocol','Field-1','Field-2','Description','Created Time')
			for nsgID in the.networks[service].keys():
				for sr in the.networks[service][nsgID]:
					if sr[0]: auditIssuesFound=True
					writeRow([nsgID, sr[1], sr[2], sr[3], sr[4], sr[5], sr[6], sr[7], sr[8], sr[9]], style=getStyle(risk=sr[0], f6=[0]))
			finalTouchTable()
				
			service='nsg_vnics'
			row+=1
			addHeading2('NSG - VNICs', hx='h3')
			generateHeaderList('NSG OCID','Parent resource OCID','VNIC OCID','Time Associated')
			for nsgID in the.networks[service].keys():
				for v in the.networks[service][nsgID]: data.append([nsgID, v[0], v[1], v[2]])
			addTable()
		
		service='Internet Gateway'
		if service in nwSerSel:
			addTab('IG', colWidths=[20,30,20,12,10,18], tabColor='#632523')
			addHeading2(service+'s')
			generateHeaderList('VCN OCID','Name','OCID','State','Enabled','Created Time')
			for vcnID in the.networks[service].keys():
				for ig in the.networks[service][vcnID]: data.append([vcnID, ig[0], ig[1], ig[2], ig[3], ig[4]])
			addTable()
			
		service='NAT Gateway'
		if service in nwSerSel:
			addTab('NG', colWidths=[20,30,20,12,10,17,18], tabColor='#632523')
			addHeading2(service+'s')
			generateHeaderList('VCN OCID','Name','OCID','State','Block Traffic','Public IP Address','Created Time')
			for vcnID in the.networks[service].keys():
				for nat in the.networks[service][vcnID]: data.append([vcnID, nat[0], nat[1], nat[2], nat[3], nat[4], nat[5]])
			addTable()
		
		service='Service Gateway'
		if service in nwSerSel:
			addTab('SG', colWidths=[20,30,20,12,40,20,12,18], tabColor='#632523')
			addHeading2(service+'s')
			generateHeaderList('VCN OCID','Name','OCID','State','Services','Route Table OCID','Block Traffic','Created Time')
			for vcnID in the.networks[service].keys():
				for sg in the.networks[service][vcnID]: data.append([vcnID, sg[0],sg[1],sg[2],sg[3],sg[4],sg[5],sg[6]])
			addTable()

		service="VCN's DRG"
		service1="Dynamic Routing Gateway"
		if service in nwSerSel or service1 in nwSerSel:
			addTab('DRG', colWidths=[20,20,30,20,12,18,20], tabColor='#632523')
			if service in nwSerSel:
				addHeading2(service+'s')
				generateHeaderList('VCN OCID','DRG OCID','Name','Route Table OCID','State','Created Time')
				for vcnID in the.networks[service].keys():
					for att in the.networks[service][vcnID]: data.append([vcnID, att[0],att[1],att[2],att[3],att[4]])
				addTable()
			service=service1; row+=1
			if service in nwSerSel:
				addHeading2(service+'s')
				writeHeader('Tenancy','Compartment','Name','DRG OCID','State','Region','Created Time')
				for t in sorted(the.networks[service].keys()):
					for r in sorted(the.networks[service][t].keys()):
						for c in sorted(the.networks[service][t][r].keys()):
							for n in sorted(the.networks[service][t][r][c].keys()):
								drg=the.networks[service][t][r][c][n]
								writeRow(data=[t,c,n,drg[0],drg[1],r,drg[2]], style=getStyle(f6=[3]))
				finalTouchTable()

		service="Local Peering Gateway"
		if service in nwSerSel:
			addTab('LPG', colWidths=[20,25,12,15,20,18,15,18], tabColor='#632523')
			if service in nwSerSel:
				addHeading2(service+'s')
				generateHeaderList('VCN OCID','Name','State','Peering Status','Route Table OCID','Peer Advertised CIDR','Cross-Tenancy','Created Time')
				for vcnID in the.networks[service].keys():
					for obj in the.networks[service][vcnID]: data.append([vcnID, obj[0],obj[1],obj[2],obj[3],obj[4],obj[5],obj[6]])
				addTable()
		
	if ui.parentWindow.m_checkBox_CloudGuard.GetValue():
		service="Problems"
		addTab(service, colWidths=[14,20,22,18,20,25,15,12,18,18], tabColor='#F08080')
		addHeading2(service)
		writeHeader('Tenancy','Compartment','Labels','State','Regions(Affected)','Resource Name','Resource Type','Risk','First Found On','Last Found On')
		for t in the.cloudGuard[service].keys():
			for c in the.cloudGuard[service][t].keys():
				for pr in the.cloudGuard[service][t][c]: writeRow([t,c, pr[0],pr[1],pr[2],pr[3],pr[4],pr[5],pr[6],pr[7]], getStyle(risk=pr[5]))
		finalTouchTable()
		
		service="Recommendations"
		addTab(service, colWidths=[14,20,18,20,12,10,35,25,18,18], tabColor='#F08080')
		addHeading2(service)
		writeHeader('Tenancy','Compartment','State','Type','Risk','Count','Name','Details','Created On','Updated On')
		for t in the.cloudGuard[service].keys():
			for c in the.cloudGuard[service][t].keys():
				for rc in the.cloudGuard[service][t][c]: writeRow([t,c, rc[0],rc[1],rc[2],rc[3],rc[4],rc[5],rc[6],rc[7]], getStyle(risk=rc[2]))
		finalTouchTable()
	if False:
		# usages[tenName][key] = [comp,rgn+' / '+ad,srv,name,' / '.join(amt,qty,shape)]
		# if True: #Todo pending # Not working for Oracle internal tenancies
			# ws = workbook.add_worksheet('Usages')
			# ws.hide_gridlines(2)
			# ws.set_column(0,0,14)
			# ws.set_column(1,1,25)
			# ws.set_column(2,4,35)
			# ws.set_column(5,5,40)
			# ws.set_column(6,6,20)
			
			# row=0
			# ws.write(row,0, 'Tenancy',format['tbl_head'])
			# ws.write(row,1, 'Compartment',format['tbl_head'])
			# ws.write(row,2, 'Region / AD',format['tbl_head'])
			# ws.write(row,3, 'Service',format['tbl_head'])
			# ws.write(row,4, 'Name',format['tbl_head'])
			# ws.write(row,5, '-',format['tbl_head'])
			# ws.write(row,6, '-',format['tbl_head'])
			# row+=1
			# ws.freeze_panes(row,0)
			
			# for t in sortedTenancies:
				# for k in sorted(usages[t].keys()):
					# # creatDate=the.dateFormat(users[t][k][4])
					# cl_format = format['tblCell']
					# cl_format_small = format['tblCell_f8']
					# ws.write(row,0, t, cl_format)
					# ws.write(row,1, usages[t][k][0], cl_format)
					# ws.write(row,2, usages[t][k][1], cl_format)
					# ws.write(row,3, usages[t][k][2], cl_format)
					# ws.write(row,4, usages[t][k][3], cl_format)
					# ws.write(row,5, usages[t][k][4], cl_format)
					# ws.write(row,6, usages[t][k][5], cl_format)
					# row+=1
			# ws.autofilter(0, 0, row-1, 6)
			# addCountSummary(row+2, usages)
		pass
	
	# if len(workbook.worksheets())>0: # If no worksheet created, then excel file will not be saved
	workbook.close()
	reportsString='Generated Excel Report placed in ".\\' + conf.resDr + '\\" folder.'
	ui.parentWindow.gauge.SetValue(100)
	ui.setInfo('Job Completed.  ' + reportsString)
		
	if ui.commandlineMode: # Commandline Mode
		if the.sendMail:
			sendMail=False
			if 'sendmail_onlyif_audit_issues' not in conf.keys: sendMail=True # Default, send mail even if audit issues not found
			elif auditIssuesFound: sendMail=True # send mail only if audit issues found
			if sendMail:
				ui.setInfo('Sending generated report via email..')
				import mail
				mail.init(conf, the)
				mail.sendMail(attachmentDir=reportDirPath, attachmentName=reportName, tenancies=sortedTenancies)
		sleep(5)
		os._exit(0)
	else: # Normal GUI mode
		wx=ui.wx
		dlg=wx.MessageDialog(ui.parentWindow, "Job Completed.\n\n" + reportsString, 'Done', wx.YES_NO | wx.CANCEL | wx.NO_DEFAULT | wx.ICON_INFORMATION)
		dlg.SetYesNoCancelLabels("&OK", "Open &Report", "&Close")
		ans=dlg.ShowModal()
		if ans==wx.ID_NO:
			os.startfile('"' + reportPath + '"')
		elif ans==wx.ID_CANCEL:
			os._exit(0)

def generateHeaderList(*headers):
	global data,head
	data=[]
	head=[]
	for h in headers:
		f={'header': h,'header_format':format['tbl_head'],'format':format['tblCell']} #format['font_10']
		if 'OCID' in h: f['format']=format['tblCell_f6']
		head.append(f)
	#print('Debug| Service1: ' + service)
	#print(head)
def writeHeader(*headers):
	global row,startRow,cols
	startRow=row
	i=0
	for h in headers:
		ws.write(row,i,h,format['tbl_head'])
		i+=1
	cols=i
	row+=1
def writeRow(data=[], style=[]):
	global row
	i=0
	for d in data:
		ws.write(row,i, d, format[style[i]])
		i+=1
	row+=1
def getStyle(risk='', f6=[]):
	rs = '_'+risk.lower()[0:3] if risk else '' # first three characters of, risk string
	norm = 'tblCell'+rs; normS = norm+'_f6'
	style=[]
	for i in range(0,cols): style.append(normS if i in f6 else norm)
	return style
def finalTouchTable():
	global row
	ws.autofilter(startRow, 0, row-1, cols-1)
	if row==startRow+1: ws.write(row,0,'No data found !',format['normal']) # means no data, row still at first line
	row+=1
def addTab(name, tabColor='#FFFFFF', colWidths=[]):
	global ws,row
	row=0
	ws = workbook.add_worksheet(name)
	ws.hide_gridlines(2)
	ws.set_tab_color(tabColor)
	i=0
	for cw in colWidths:
		ws.set_column(i,i,cw)
		i+=1
def addTable():
	global startRow,row,data,head,service
	dataLen = len(data)
	if dataLen>0:
		startRow=row
		endRow = startRow + dataLen
		endCol = len(data[0]) - 1
		name=re.sub(r"[\s\'\(\)]", '', service)
		ws.add_table(startRow, 0, endRow, endCol, {'data':data, 'columns':head, 'banded_rows':False, 'name':name, 'style':'Table Style Medium 15'})
		row=endRow
	else:
		ws.write(row,0, 'No data found !', format['normal'])
	row+=1
def addHeading2(heading, hx='h2'):
	global row
	ws.merge_range(row,0,row,3,heading,format[hx])
	row+=1
def addAllFormatsToWorkbook():
	f={
		'normal' : {},
		'bold' : {'bold':True},
		'bold_underlined' : {'bold':True, 'underline':True},
		'bold_italic' : {'bold':True, 'italic':True},
		'italic_underlined' : {'underline':True, 'italic':True},
		'font_10' : {'font_size':10},
		'normal_small' : {'font_size':8},
		'italic' : {'italic':True},
		'italic_left' : {'italic':True, 'align':'left'},
		'italic_downBorder' : {'italic':True, 'bottom':1},
		'center' : {'align':'center'},
		'bold_fntRed' : {'bold':True, 'font_size':11, 'font_color':'red'},
		'fntPaleRed'  : {'font_size':10, 'font_color':'#FF3300'},
		'fntRed'      : {'font_size':10, 'font_color':'red'},
		'tbl_head'  : {'bold':True, 'bg_color':'#BDD7EE', 'font_color':'#000000', 'border':1, 'align':'left'},
		'tblCell'    :                       {'border':1, 'align':'left', 'valign':'vcenter'},
		'tblCell_cri': {'bg_color':'#FF5229', 'border':1, 'align':'left', 'valign':'vcenter'},
		'tblCell_hig': {'bg_color':'#F08080', 'border':1, 'align':'left', 'valign':'vcenter'},
		'tblCell_med': {'bg_color':'#ffff60', 'border':1, 'align':'left', 'valign':'vcenter'},
		'tblCell_low': {'bg_color':'#a0ec6e', 'border':1, 'align':'left', 'valign':'vcenter'},
		'tblCell_min': {'bg_color':'#e5fad6', 'border':1, 'align':'left', 'valign':'vcenter'},
		'tblCell_yl_rd' : {'bg_color':'#FFFF00', 'font_color':'#FF0000', 'bold':True, 'border':1, 'align':'left'},
		'tblCell_rd' : {'font_color':'#FF0000', 'bold':True, 'border':1, 'align':'left'},
		'tblCell_br' : {'font_color':'#8B2500', 'bold':True, 'border':1, 'align':'left'},
		'tblCell_bold' : {'bold':True, 'border':1, 'align':'left'},
		'tblCell_bold1' : {'bold':True, 'border':1},
		'h1' : {'font_size':14, 'font_color':'#1f497d', 'font_name':'Cambria'},
		'h2' : {'font_size':15, 'bold':True, 'font_color':'#1f497d', 'bottom':2, 'bottom_color':'#1f497d'},
		'h3' : {'font_size':13, 'bold':True, 'font_color':'#000000', 'bottom':2, 'bottom_color':'#1f497d'},
	}
	def addSmaller(siz):
		for n in ['tblCell','tblCell_cri','tblCell_hig','tblCell_med','tblCell_low','tblCell_min']:
			n1=n+'_f'+str(siz)
			f[n1]={**f[n], 'font_size':siz}
			f[n+'_wrap'] ={**f[n],  'text_wrap':1} # add also wraps
			f[n1+'_wrap']={**f[n1], 'text_wrap':1}
	addSmaller(8)
	addSmaller(6)
	format={}
	for n in f.keys(): format[n]=workbook.add_format(f[n])
	return format
#