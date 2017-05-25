#!/usr/bin/python3

from renderlib import *
from easing import *
from hashlib import sha1

# URL to Schedule-XML
scheduleUrl = 'http://sha2017.org/thereisnoscheduleyet.xml'


def introFrames(args):
    colors = (
            ('color1', 'style', 'fill', '#' + args['$color1']),
            ('color2', 'style', 'fill', '#' + args['$color2']),
            ('color3', 'style', 'fill', '#' + args['$color3']),
            ('color4', 'style', 'fill', '#' + args['$color4']),
            ('color5', 'style', 'fill', '#' + args['$color5']),
            ('color6', 'style', 'fill', '#' + args['$color6'])
    )

    #fade in title
    frames = 3 * fps
    for i in range(0, frames):
        yield(
                ('title', 'style', 'opacity', easeInQuad(i, 0, 1, frames)),
        ) + colors

    # fade in subtitle and names
    frames = 1 * fps
    for i in range(0, frames):
        yield(
            ('title', 'style', 'opacity', 1),
            ('subtitle',    'style', 'opacity', easeInQuad(i, 0, 1, frames)),
            ('personnames', 'style', 'opacity', easeInQuad(i, 0, 1, frames)),
        ) + colors

    # show whole image for 2 seconds
    frames = 2 * fps
    for i in range(0, frames):
        yield(
            ('title', 'style', 'opacity', 1),
            ('personnames', 'style', 'opacity', 1),
            ('subtitle', 'style', 'opacity', 1),
        ) + colors


def backgroundFrames(parameters):
    frames = 5 * fps
    for i in range(0, frames):
        yield(
            ('logo', 'style', 'opacity', 1),
        )


def outroFrames(args):
    frames = 2 * fps
    for i in range(0, frames):
        yield(
            ('logo',    'style', 'opacity', 1),
            ('sublogo', 'style', 'opacity', 1),
            ('cclogo',  'style', 'opacity', 1),
        )

    # fade out
    frames = 3 * fps
    for i in range(0, frames):
        yield(
            ('logo', 'style', 'opacity', "%.4f" %
             easeInCubic(i, 1, -1, frames)),
            ('sublogo', 'style', 'opacity', "%.4f" %
             easeInCubic(i, 1, -1, frames)),
            ('cclogo', 'style', 'opacity', "%.4f" %
             easeInCubic(i, 1, -1, frames)),
        )


def pauseFrames(args):
    #fade in pause
    frames = 4 * fps
    for i in range(0, frames):
        yield(
            ('pause',  'style', 'opacity', "%.4f" %
             easeInCubic(i, 0.2, 1, frames)),
        )

    # fade out
    frames = 4 * fps
    for i in range(0, frames):
        yield(
            ('pause',  'style', 'opacity', "%.4f" %
             easeInCubic(i, 1, -0.8, frames)),
        )


def debug():
    title = 'Still Recording Anyway?'

    hashed = sha1(title.encode('UTF-8')).hexdigest()

    render('intro.svg',
           '../intro.ts',
           introFrames,
           {
               '$id': 2017,
               '$title': title,
               '$subtitle': 'Look.... thinking of good jokes is difficult',
               '$personnames':  'C3VOC & Productiehuis',
               '$color1': hashed[0:6],
               '$color2': hashed[6:12],
               '$color3': hashed[12:18],
               '$color4': hashed[18:24],
               '$color5': hashed[24:30],
               '$color6': hashed[30:36],
               '$modulu': hashed[36:40]
           }
    )

    render(
        'outro.svg',
        '../outro.ts',
        outroFrames
    )

    render(
        'background.svg',
        '../background.ts',
        backgroundFrames
    )

    render(
        'pause.svg',
        '../pause.ts',
        pauseFrames
    )


def tasks(queue, args, idlist, skiplist):
    # iterate over all events extracted from the schedule xml-export
    for event in events(scheduleUrl):
        if not (idlist == []):
            if 000000 in idlist:
                print("skipping id (%s [%s])" % (event['title'], event['id']))
                continue
            if int(event['id']) not in idlist:
                print("skipping id (%s [%s])" % (event['title'], event['id']))
                continue

    hashed = sha1(event['id'].encode('utf-8')).hexdigest()

    # generate a task description and put them into the queue
    queue.put(Rendertask(
        infile='intro.svg',
        outfile=str(event['id']) + ".ts",
        sequence=introFrames,
        parameters={
            '$id': event['id'],
            '$title': event['title'],
            '$subtitle': event['subtitle'],
            '$personnames': event['personnames'],

            # Colors
            '$color1': hashed[0:6],
            '$color2': hashed[6:12],
            '$color3': hashed[12:18],
            '$color4': hashed[18:24],
            '$color5': hashed[24:30],
            '$color6': hashed[30:36],
            '$modulu': hashed[36:40]
        }
    ))

    # place a task for the outro into the queue
    if not "out" in skiplist:
        queue.put(Rendertask(
            infile='outro.svg',
            outfile='outro.ts',
            sequence=outroFrames
        ))

    # place the pause-sequence into the queue
    if not "pause" in skiplist:
        queue.put(Rendertask(
            infile='pause.svg',
            outfile='pause.ts',
            sequence=pauseFrames
        ))

    # place the background-sequence into the queue
    if not "bg" in skiplist:
        queue.put(Rendertask(
            infile='background.svg',
            outfile='background.ts',
            sequence=backgroundFrames
        ))
