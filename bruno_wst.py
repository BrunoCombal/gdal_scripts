def wst(num):
	num = '{}'.format(int(num))
	newString = ''

	for ii, ipos in zip(num[::-1], range(1, len(num)+1)):
		if ipos % 3 == 0:
			newString = ' '+ ii + newString
		else:
			newString = ii + newString

	return newString



a='12324567'
for a in ['1', '12', '123', '1234', '12345', '123456', '1234567','12345678','12345678901234567890']:
	print a,'-->', wst(a)
	