// Таймлайн ролика 04-varany. Сгенерировано scripts/prepare.py - править plan.json, не этот файл.
import slova from './slova.json';
import abzacy from './abzacy.json';

export const FPS = 30;
export type Word = {w: string; s: number; e: number; p: number};
export const WORDS: Word[] = slova as Word[];
const ABZ = abzacy as {n: number; s: number; e: number}[];
export const VOICE_SEC = ABZ[ABZ.length - 1].e;
const at = (p: number) => ABZ[p - 1].s;

export const PLAN: [number, string[]][] = [
	[1, ['komodo-01', 'komodo-02']],
	[2, ['komodo-03', 'monitor-tongue-01', 'chameleon-03', 'iguana-03']],
	[3, ['komodo-01@5', 'komodo-island-01', 'komodo-04', 'komodo-island-02']],
	[4, ['monitor-tongue-01', 'monitor-tongue-01@15', 'monitor-02', 'monitor-tongue-01@28']],
	[5, ['komodo-03', 'komodo-02@4', 'komodo-04@8']],
	[6, ['komodo-01@9', 'komodo-03@10', 'komodo-02', 'komodo-04@3']],
	[7, ['desert-01', 'monitor-04', 'desert-02', 'monitor-03', 'monitor-04@12']],
	[8, ['water-monitor-01', 'monitor-02', 'water-monitor-01@12', 'monitor-tongue-01@20']],
	[9, ['chameleon-01', 'chameleon-03', 'chameleon-02', 'chameleon-01@30']],
	[10, ['chameleon-06', 'chameleon-05', 'chameleon-04', 'chameleon-07']],
	[11, ['marine-iguana-01', 'sea-01']],
	[12, ['iguana-01', 'iguana-02', 'iguana-03', 'iguana-02@60']],
	[13, ['komodo-02', 'komodo-01@3', 'komodo-04', 'komodo-03@5', 'komodo-01@10']],
	[14, ['komodo-01', 'chameleon-03', 'iguana-03', 'monitor-tongue-01@5']],
];
const key = (c: string) => c.replace('@', '_');
export const SHOTS: [string, number][] = PLAN.flatMap(([p, clips]) => {
	const a = at(p);
	const b = p < ABZ.length ? at(p + 1) : VOICE_SEC;
	return clips.map((c, i) => [key(c.includes('@') ? c : c + '@0'), a + ((b - a) * i) / clips.length] as [string, number]);
});

export const CHAPTERS = (
	[
		[3, 'Комодский варан'],
		[4, 'Нюхает языком'],
		[5, 'Обед на год'],
		[6, 'Яд'],
		[7, 'Варан в Казахстане'],
		[8, 'Водяной варан'],
		[9, 'Язык хамелеона'],
		[10, 'Глаза хамелеона'],
		[11, 'Морская игуана'],
		[12, 'Третий глаз'],
	] as [number, string][]
).map(([p, title]) => ({p, title, at: at(p) + 0.1}));

export const PLATES = [1, ABZ.length];

export const SHORTS: {id: string; from: number; to: number; title: string; outro?: string; ask?: string}[] = [{id: 'Short-bez-samca', from: 213.60, to: 250.30, title: 'Комодский варан', outro: 'Полное видео - на канале', ask: 'Про какого зверя рассказать дальше?'}, {id: 'Short-kazakhstan', from: 92.20, to: 117.22, title: 'Варан в Казахстане', outro: 'Полное видео - на канале', ask: 'Видел варана вживую? Пиши где'}, {id: 'Short-obed', from: 55.56, to: 71.61, title: 'Обед варана', outro: 'Полное видео - на канале', ask: 'Какой зверь из ролика удивил больше всех?'}, {id: 'Short-hameleon', from: 130.07, to: 151.38, title: 'Хамелеон', outro: 'Полное видео - на канале', ask: 'Знал, что язык хамелеона длиннее тела?'}, {id: 'Short-iguana', from: 176.17, to: 200.01, title: 'Морская игуана', outro: 'Полное видео - на канале', ask: 'Слышал об этом раньше? Пиши'}];

export const COVER = {clip: 'komodo-01_0', sec: 3, small: 'Детёныши', big: 'без самца'};
