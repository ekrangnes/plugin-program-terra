j=0

for i in range(1,32*3,3):
	print("<setting id='dev"+str(j)+"PlaybackPlaying' type='bool' label='"+str(31100+j)+"' visible='gt(-"+str(i)+","+str(j)+")+eq(-"+str(i+1)+",true)' default='false' />")
	print("<setting id='dev"+str(j)+"PlaybackPaused' type='bool' label='"+str(31132+j)+"' visible='gt(-"+str(i+)+","+str(j)+")+eq(-3,true)' default='false' />")
	print("<setting id='dev"+str(j)+"PlaybackStopped' type='bool' label='"+str(31164+j)+"' visible='gt(-3,"+str(j)+")+eq(-2,true)' default='false' />")

	j+=1
	
		<setting id="dev0PlaybackPlaying" label="31100" type="bool" visible="gt(-1,0)+eq(-2,true)" default="false"/>
		<setting id="dev0PlaybackPaused" label="31132" type="bool" visible="gt(-2,0)+eq(-3,true)" default="false"/>
		<setting id="dev0PlaybackStopped" label="31164" type="bool" visible="gt(-3,0)+eq(-4,true)" default="false"/>