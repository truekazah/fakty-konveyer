// Таймлайн ролика 01-skorost. Сгенерировано scripts/prepare.py - править plan.json, не этот файл.
import slova from './slova.json';
import abzacy from './abzacy.json';

export const FPS = 30;
export type Word = {w: string; s: number; e: number; p: number};
export const WORDS: Word[] = slova as Word[];
const ABZ = abzacy as {n: number; s: number; e: number}[];
export const VOICE_SEC = ABZ[ABZ.length - 1].e;
const at = (p: number) => ABZ[p - 1].s;

export const PLAN: [number, string[]][] = [
	[1, ['cheetah-running-03', 'sports-car-03']],
	[2, ['cheetah-02', 'falcon-flying-01', 'ostrich-running-03']],
	[3, ['falcon-diving-02', 'falcon-flying-01@3', 'falcon-diving-03', 'bird-flying-01']],
	[4, ['swift-bird-03', 'swift-bird-03@10']],
	[5, ['fish-school-hunting-01', 'marlin-fish-03', 'fish-school-hunting-02']],
	[6, ['pronghorn-antelope-01', 'pronghorn-antelope-03', 'pronghorn-antelope-01@10']],
	[7, ['ostrich-running-03', 'ostrich-running-01', 'ostrich-running-02', 'ostrich-running-03@5']],
	[8, ['sprinter-running-track-01', 'cheetah-sprint-02', 'sprinter-running-track-02', 'cheetah-sprint-03']],
	[9, ['snail-01', 'snail-03', 'snail-02']],
	[10, ['sloth-03', 'sloth-01', 'sloth-02']],
	[11, ['ant-macro-01', 'ant-macro-02', 'ants-01@8']],
	[12, ['cheetah-sprint-01', 'cheetah-03', 'cheetah-running-03@4', 'cheetah-02@6']],
	[13, ['cheetah-chasing-01', 'sports-car-02', 'sports-car-03', 'cheetah-running-01', 'cheetah-sprint-01@6']],
	[14, ['cheetah-02@10', 'sports-car-01']],
];
const key = (c: string) => c.replace('@', '_');
export const SHOTS: [string, number][] = PLAN.flatMap(([p, clips]) => {
	const a = at(p);
	const b = p < ABZ.length ? at(p + 1) : VOICE_SEC;
	return clips.map((c, i) => [key(c.includes('@') ? c : c + '@0'), a + ((b - a) * i) / clips.length] as [string, number]);
});

export const CHAPTERS = (
	[
		[3, 'Сапсан'],
		[4, 'Стриж'],
		[5, 'Рыба-парусник'],
		[6, 'Вилорогая антилопа'],
		[7, 'Страус'],
		[8, 'Человек'],
		[9, 'Улитка'],
		[10, 'Ленивец'],
		[11, 'Муравей-челюстник'],
		[12, 'Гепард'],
	] as [number, string][]
).map(([p, title]) => ({p, title, at: at(p) + 0.1}));

export const PLATES = [1, ABZ.length];

export const SHORTS: {id: string; from: number; to: number; title: string; outro?: string; ask?: string}[] = [{id: 'Short-sapsan', from: 17.27, to: 35.19, title: 'Сапсан', outro: 'Полное видео - на канале'}, {id: 'Short-straus', from: 84.76, to: 102.60, title: 'Страус', outro: 'Полное видео - на канале'}, {id: 'Short-bolt', from: 101.05, to: 124.61, title: 'Усэйн Болт', outro: 'Полное видео - на канале'}, {id: 'Short-gepard', from: 166.74, to: 207.97, title: 'Гепард', outro: 'Полное видео - на канале'}];

export const COVER = {clip: 'cheetah-running-03_0', sec: 3, small: 'Гепард', big: 'быстрее спорткара'};
