# coding=utf-8
'''
解析whois信息里的省市信息
'''
import sys
import MySQLdb
import traceback
from qianduan_format import WebFormat

reload(sys)
sys.setdefaultencoding('utf-8')

class Whois2Addr(object):
	def __init__(self):
		self.mohu = [('s', 'sh'), ('sh', 's'), ('z', 'zh'), ('zh', 'z'), ('s', 'c'), ('c', 's'), ('en', 'eng'),
					 ('an', 'ang'), ('eng', 'en'), ('ang', 'an'), ('c', 'ch'), ('ch', 'c'), ('uo', 'ou'), ('ia', 'ai'),
					 ('ie', 'ei'), ('fu', 'fo'), ('fo', 'fu'), ('ing', 'in'), ('in', 'ing'), ('shi', '')]  # 模糊音定义
		# 连接数据库
		self.connA = MySQLdb.connect(
			host='172.26.253.3',
			port=3306,
			user='root',
			passwd='platform'
		)
		self.connA.set_character_set('utf8')
		self.curA = self.connA.cursor()
		self.curA.execute("SET NAMES utf8")
		self.curA.execute("use location;")
		self.connA.commit()

	# flag设计:    p: 1正常  2写反  5写错      c: 10正常  20写反  30写错
	def filter_no_num(self, n):
		if n not in '0123456789\\"\'':
			return True

	# 匹配省
	def match_province(self, province, flag):
		str1 = 'select name, id from location.district WHERE parentid = 0 AND (pinyin = "%s" OR initials = "%s" OR locate(name, "%s"))' % (
		province, province, province)  # 寻找省份
		if self.curA.execute(str1) != 0:
			# 存在
			r_province = self.curA.fetchone()
			# r_province_name = r_province[1]
			# r_province_num = r_province[2]
			return r_province
		else:
			return None, 0

	# 匹配市
	def match_city(self, r_province_num, city, flag):
		r_city_name = ''
		str2 = 'select id, name from location.district WHERE parentid = %d AND (pinyin = "%s" OR initials = "%s" OR locate(name, "%s"))' % (
		r_province_num, city, city, city)  # 寻找城市
		if self.curA.execute(str2) != 0:
			r_city = self.curA.fetchone()
			r_city_name = r_city[1]
		else:
			# 不存在市，从县一级寻找
			str3 = 'select id, name from location.district WHERE parentid = %d' % (r_province_num)
			self.curA.execute(str3)
			r_city_list = self.curA.fetchall()
			for t in r_city_list:
				if t[0] is not None:
					str4 = 'select id, name from location.district WHERE parentid = %d AND (pinyin = "%s" OR initials = "%s" OR locate(name, "%s"))' % (
					t[0], city, city, city)
					if self.curA.execute(str4) != 0:
						r_county = self.curA.fetchone()
						r_city_name = "%s" % t[1]
						break
		if r_city_name:
			return r_city_name
		else:
			return None

	def match_error1(self, province, city, flag):
		str1 = 'select F.id, C.name, F.name from location.district AS C, location.district AS F WHERE C.order = 1 AND C.pinyin = "%s" AND F.id = C.parentid' % (
		province)  # 寻找省份
		if self.curA.execute(str1) != 0:

			r_province = self.curA.fetchone()
			r_province_name = r_province[2]
			r_province_num = r_province[0]
			r_city_name = None
			str2 = 'select id, name from location.district WHERE parentid = %d AND (pinyin = "%s" OR initials = "%s" OR locate(name, "%s"))' % (
			r_province_num, city, city, city)  # 寻找城市
			if self.curA.execute(str2) != 0:
				r_city = self.curA.fetchone()
				r_city_name = r_city[1]
			else:
				# 不存在市，从县一级寻找
				str3 = 'select id, name from location.district WHERE parentid = %d' % (r_province_num)
				self.curA.execute(str3)
				r_city_list = self.curA.fetchall()
				for t in r_city_list:
					if t[0] is not None:
						str4 = 'select id, name from location.district WHERE parentid = %d AND (pinyin = "%s" OR initials = "%s" OR locate(name, "%s"))' % (
						t[0], city, city, city)
						if self.curA.execute(str4) != 0:
							r_county = self.curA.fetchone()
							r_city_name = "%s" % t[1]
							break
			# curB.execute('update whois_zgx_temp set reg_city_detail = "%s_%s" WHERE domain = "%s"' % (r_province_name, r_city_name, domain))
			# curB.execute('update whois_zgx_temp set reg_city_detail_flag = %d WHERE domain = "%s"' % (flag, domain))
			return r_province_name, r_city_name, flag
		else:
			return None

	# 模糊音匹配方法
	def match_error2(self, province1, city1, flag):
		for t in self.mohu:
			province = province1.replace(t[1], t[0])
			city = city1.replace(t[1], t[0])
			str1 = 'select id, name, district.order from district WHERE parentid = 0 AND \
			 (replace(replace(replace(replace(replace(replace(pinyin,"sh","s"),"zh","z"),"ch","c"),"ing","in"),"eng","en"),"ang","an")="%s")' % (
			province)  # 寻找省份

			if self.curA.execute(str1) != 0:
				# 存在
				r_province = self.curA.fetchone()
				r_province_name = r_province[1]
				r_province_num = r_province[2]
				r_city_name = None
				str2 = 'select id, name from location.district WHERE parentid = %d AND (replace(replace(replace(replace(replace(replace(pinyin,"sh","s"),"zh","z"),"ch","c"),"ing","in"),"eng","en"),"ang","an") = "%s")' % (
				r_province_num, city)  # 寻找城市
				if self.curA.execute(str2) != 0:
					r_city = self.curA.fetchone()
					r_city_name = r_city[1]
				else:
					# 不存在市，从县一级寻找
					str3 = 'select id, name from location.district WHERE parentid = %d' % (r_province_num)
					self.curA.execute(str3)
					r_city_list = self.curA.fetchall()
					for t in r_city_list:
						if t[0] is not None:
							str4 = 'select id, name from location.district WHERE parentid = %d AND (replace(replace(replace(replace(replace(replace(pinyin,"sh","s"),"zh","z"),"ch","c"),"ing","in"),"eng","en"),"ang","an") = "%s")' % (
							t[0], city)
							if self.curA.execute(str4) != 0:
								r_county = self.curA.fetchone()
								r_city_name = "%s" % t[1]
								break
				# curB.execute('update whois_zgx_temp set reg_city_detail = "%s_%s" WHERE domain = "%s"' % (r_province_name, r_city_name, domain))
				# curB.execute('update whois_zgx_temp set reg_city_detail_flag = %d WHERE domain = "%s"' % (flag, domain))
				return r_province_name, r_city_name, flag
			else:
				return None

	def analyze(self, province, city):
		# 获取未解析的域名及其whois信息
		detail = ''
		# print src
		if province is None:
			province = ''
		else:
			province = province.lower().replace(' ', '')
		if city is None:
			city = ''
		else:
			city = city.lower().replace(' ', '')
		province_sheng = 'nodata'
		city_shi = 'nodata'
		province = filter(self.filter_no_num, province)  # 过滤数字和特殊字符
		city = filter(self.filter_no_num, city)  # 过滤数字和特殊字符
		f = 1
		# 匹配省
		r_province = self.match_province(province, f)
		if r_province[0] is None:
			if province != '':
				# 去掉末尾的省市字样以及特殊匹配
				for t in [('tebiexingzhengqu', ''), ('zhuangzuzizhiqu', ''), ('huizuzizhiqu', ''),
						  ('weiwuerzizhiqu', ''), ('zizhiqu', ''), ('sheng', ''), ('shi', ''), ('province', ''),
						  ('city', ''), ('xian', ''), ('qu', ''), ('zzzzq', ''), ('tbxzq', ''), ('hzzzq', ''),
						  ('wwezzq', ''), ('wwezzzq', '')]:
					if t[0] in province:
						province = province.replace(t[0], t[1])
						break
				if province == 'hongkang' or province == 'xianggang':  # 用错的人比较多
					f = 5
					province = 'hongkong'
				elif province[-16:] == 'weiwuerzuzizhiqu':
					province = province[:-16]
				elif province[-1:] == 's':
					province = province[:-1]
			r_province = self.match_province(province, f)
			if r_province[0] is None:
				# 省市写反
				r_province = self.match_province(city, 2)
				f = 2
				if r_province[0] is None:
					result = self.match_error1(province, city, 3)
					if result is None:
						# 模糊音
						result = self.match_error2(province, city, 4)
						if result is None:
							if province in ['other', 'others', 'qita', 'china', 'cn']:
								return None, None, -1
							# curB.execute('update whois_zgx_temp set reg_city_detail_flag = %d WHERE domain = "%s"' % (-1, domain))
							else:
								return None, None, 0
							# curB.execute('update whois_zgx_temp set reg_city_detail_flag = %d WHERE domain = "%s"' % (0, domain))
						else:
							return result
					else:
						return result
				# others

				else:  # fan
					# city
					f = f % 10 + 2 * 10
					r_city = self.match_city(r_province[1], province, f)
					if r_city is None:
						if city != '':
							for t in [('wulumuqi', 'urumqi'), ('kelamayi', 'karamay'), ('bayinguoleng', 'bayingol'),
									  ('akesu', 'aksu'), ('kezilesu', 'kizilsu'), ('kashi', 'kashgar'),
									  ('hetian', 'hotan'), ('yili', 'ili'), ('aletai', 'altay'), ('alaer', 'aral'),
									  ('tumushuke', 'tumsuk'), ('kuerle', 'korla'), ('tulufan', 'turfan')]:
								if t[0] in city:
									city = t[1]
									f = f % 10 + 3 * 10
									break
							if city[-3:] == 'shi':
								city = city[:-3]
							elif city[-4:] == 'xian':
								city = city[:-4]
							elif city[-4:] == 'diqu':
								city = city[:-4]
							elif city[-2:] == 'qu':
								city = city[:-2]
							elif city[-9:] == 'zizhizhou':
								city = city[:-9]
							elif city == 'hongkang' or city == 'xianggang':
								city = 'hongkong'
								f = f % 10 + 3 * 10
							elif 'urumchi' in city:
								city = 'urumqi'
							elif city[-1:] == 's' and len(city) <= 4:
								city = city[:-1]

						r_city = self.match_city(r_province[1], city, f)
						return r_province[0], r_city, f
					# curB.execute('update whois_zgx_temp set reg_city_detail = "%s_%s", reg_city_detail_flag = %d WHERE domain = "%s"' % (r_province[0], r_city, f, domain))
					else:
						return r_province[0], r_city, f
					# curB.execute('update whois_zgx_temp set reg_city_detail = "%s_%s", reg_city_detail_flag = %d WHERE domain = "%s"' % (r_province[0], r_city, f, domain))
			else:
				# city
				f = f % 10 + 1 * 10
				r_city = self.match_city(r_province[1], city, f)
				if r_city is None:
					if city != '':
						for t in [('wulumuqi', 'urumqi'), ('kelamayi', 'karamay'), ('bayinguoleng', 'bayingol'),
								  ('akesu', 'aksu'), ('kezilesu', 'kizilsu'), ('kashi', 'kashgar'), ('hetian', 'hotan'),
								  ('yili', 'ili'), ('aletai', 'altay'), ('alaer', 'aral'), ('tumushuke', 'tumsuk'),
								  ('kuerle', 'korla'), ('tulufan', 'turfan')]:
							if t[0] in city:
								city = t[1]
								f = f % 10 + 3 * 10
								break
						if city[-3:] == 'shi':
							city = city[:-3]
						elif city[-4:] == 'xian':
							city = city[:-4]
						elif city[-4:] == 'diqu':
							city = city[:-4]
						elif city[-2:] == 'qu':
							city = city[:-2]
						elif city[-9:] == 'zizhizhou':
							city = city[:-9]
						elif city == 'hongkang' or city == 'xianggang':
							city = 'hongkong'
							f = f % 10 + 3 * 10
						elif city[-1:] == 's' and len(city) <= 4:
							city = city[:-1]

					r_city = self.match_city(r_province[1], city, f)
					return r_province[0], r_city, f
				# curB.execute('update whois_zgx_temp set reg_city_detail = "%s_%s", reg_city_detail_flag = %d WHERE domain = "%s"' % (r_province[0], r_city, f, domain))
				else:
					f = f % 10 + 1 * 10
					return r_province[0], r_city, f
				# curB.execute('update whois_zgx_temp set reg_city_detail = "%s_%s", reg_city_detail_flag = %d WHERE domain = "%s"' % (r_province[0], r_city, f, domain))
		else:
			# city
			f = f % 10 + 1 * 10
			r_city = self.match_city(r_province[1], city, f)
			if r_city is None:
				if city != '':
					for t in [('wulumuqi', 'urumqi'), ('kelamayi', 'karamay'), ('bayinguoleng', 'bayingol'),
							  ('akesu', 'aksu'), ('kezilesu', 'kizilsu'), ('kashi', 'kashgar'), ('hetian', 'hotan'),
							  ('yili', 'ili'), ('aletai', 'altay'), ('alaer', 'aral'), ('tumushuke', 'tumsuk'),
							  ('kuerle', 'korla'), ('tulufan', 'turfan')]:
						if t[0] in city:
							city = t[1]
							f = f % 10 + 3 * 10
							break
					if city[-3:] == 'shi':
						city = city[:-3]
					elif city[-4:] == 'xian':
						city = city[:-4]
					elif city[-4:] == 'diqu':
						city = city[:-4]
					elif city[-2:] == 'qu':
						city = city[:-2]
					elif city[-9:] == 'zizhizhou':
						city = city[:-9]
					elif city == 'hongkang' or city == 'xianggang':
						city = 'hongkong'
						f = f % 10 + 2 * 10
					elif 'urumchi' in city:
						city = 'urumqi'
					elif city[-1:] == 's' and len(city) <= 4:
						city = city[:-1]

				r_city = self.match_city(r_province[1], city, f)
				return r_province[0], r_city, f
			# curB.execute('update whois_zgx_temp set reg_city_detail = "%s_%s", reg_city_detail_flag = %d WHERE domain = "%s"' % (r_province[0], r_city, f, domain))
			else:
				f = f % 10 + 1 * 10
				return r_province[0], r_city, f
			# curB.execute('update whois_zgx_temp set reg_city_detail = "%s_%s", reg_city_detail_flag = %d WHERE domain = "%s"' % (r_province[0], r_city, f, domain))


def get_pos_whois(pro,ci):
	w2a = Whois2Addr()
	flag = 0
	print pro
	print ci
	province, city, type = w2a.analyze(pro, ci)
	if province is None:
		province = ''
		flag = 2
	else:
		province = MySQLdb.escape_string(province)
	if city is None:
		city = ''
	else:
		city = MySQLdb.escape_string(city)
		flag = 1
	l = WebFormat()
	city = l.change_city(province, city)
	province = pro if province is '' else province
	city = ci if city is '' else city
	# 此处为解析之后的输出结果
	country = None
	if (province):
		country = "中国"
	print country
	print province
	print city
	print flag

#
# def analysiswho():
# 	# 连接数据库
# 	# conn = MySQLdb.connect(
# 	# 	host='172.26.253.3',
# 	# 	port=3306,
# 	# 	user='root',
# 	# 	passwd='platform'
# 	# )
# 	# conn.set_character_set('utf8')
# 	# cur = conn.cursor()
# 	# cur.execute("SET NAMES utf8")
# 	# cur.execute("use location;")
# 	# conn.commit()
# 	# sqlstr = "SELECT domain,province,city FROM mal_domain_profile.domain_locate where province is not null "
# 	# count = cur.execute(sqlstr)
# 	# if count == 0:
# 	# 	print "No domain to analyze"
# 	# 	exit(0)
# 	# w2a = Whois2Addr()
# 	# results = cur.fetchall()
# 	# cc=0
# 	for r in results:
# 		cc=cc+1
# 		flag=0
# 		domain=r[0]
# 		print domain
# 		province, city, type = w2a.analyze(r[1], r[2])
# 		if province is None:
# 			province =''
# 			flag=2
# 		else:
# 			province = MySQLdb.escape_string(province)
# 		if city is None:
# 			city =''
# 		else:
# 			city = MySQLdb.escape_string(city)
# 			flag=1
# 		try:
# 			l = WebFormat()
# 			city = l.change_city(province, city)
# 			province=r[1] if province is '' else province
# 			city=r[2] if city is '' else city
# 			#此处为解析之后的输出结果
# 			print province
# 			print city
# 			country=None
# 			if(province):
# 				country="中国"
# 			sqls="update mal_domain_profile.domain_locate set reg_whois_country=%s,reg_whois_province=%s,reg_whois_city=%s, \
# 				  reg_whois_type=%s where domain=%s"
# 			data=(country,province,city,flag,domain)
# 			cur.execute(sqls,data)
# 			if (cc == 1000):
# 				conn.commit()
# 				cc = 0
# 		except Exception, e:
# 			print e
# 			cur.rollback()
# 	conn.commit()
# 	conn.close()

if __name__ == '__main__':
	# 1为正常解析成功，2类型为无法解析
	get_pos_whois('fujian','fuzhou')