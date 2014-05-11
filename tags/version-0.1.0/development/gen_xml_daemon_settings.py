for i in range(0,32):
	print("<setting id='dev"+str(i)+"Type' type='text' visible='false' />")
	print("<setting id='dev"+str(i)+"Playing' type='labelenum' label='"+str(31030+i)+"' default='off' values='on|off' visible='eq(-1,switch)' />")
	print("<setting id='dev"+str(i)+"Playing' type='labelenum' label='"+str(31030+i)+"' default='0' values='0|12.5|25|37.5|50|62.5|75|87.5|100' visible='eq(-2,dimmer)' />")