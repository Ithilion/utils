import vapoursynth as vs

def FadeIn(c, num_fade):
	core = vs.get_core()
	fade_segment = c[:num_fade]
	blank = core.std.BlankClip(clip=c, length=1)
	fade_frames = []
	for i in range(fade_segment.num_frames):
		fade_frames.append(core.std.Merge(clipa=blank, clipb=fade_segment[i], weight=i/(fade_segment.num_frames-1)))
	return core.std.Splice(clips=fade_frames) + c[num_fade:]

def FadeOut(c, num_fade):
	core = vs.get_core()
	fade_segment = c[-num_fade:]
	blank = core.std.BlankClip(clip=c, length=1)
	fade_frames = []
	for i in range(fade_segment.num_frames):
		fade_frames.append(core.std.Merge(clipa=fade_segment[i], clipb=blank, weight=i/(fade_segment.num_frames-1)))
	return c[:-num_fade] + core.std.Splice(clips=fade_frames)

def Subtract(c1, c2, luma=126, planes=[0, 1, 2], obvious=True):
	core = vs.get_core()
	expr = ('{luma} x + y -').format(luma=luma)
	expr = [(i in planes) * expr for i in range(3)]
	ret = core.std.Expr([c1, c2], expr)
	return core.generic.Levels(ret, 127, 129, 1, 0, 255) if obvious else ret
