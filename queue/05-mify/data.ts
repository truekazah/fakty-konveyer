// Таймлайн ролика 05-mify. Сгенерировано scripts/prepare.py - править plan.json, не этот файл.
import slova from './slova.json';
import abzacy from './abzacy.json';

export const FPS = 30;
export type Word = {w: string; s: number; e: number; p: number};
export const WORDS: Word[] = slova as Word[];
const ABZ = abzacy as {n: number; s: number; e: number}[];
export const VOICE_SEC = ABZ[ABZ.length - 1].e;
const at = (p: number) => ABZ[p - 1].s;

export const PLAN: [number, string[]][] = [
	[1, ['knuckles-01', 'knuckles-02']],
	[2, ['brain-scan-01', 'carrot-02', 'kids-candy-01', 'shaving-02']],
	[3, ['mri-01', 'brain-scan-01', 'mri-02', 'brain-scan-02', 'brain-scan-03']],
	[4, ['taste-01', 'taste-02', 'taste-03', 'taste-04']],
	[5, ['carrot-01', 'old-plane-01', 'radar-01', 'night-sky-01', 'radar-02', 'carrot-02']],
	[6, ['shaving-01', 'shaving-03', 'shaving-04', 'shaving-05']],
	[7, ['nails-01', 'nails-02', 'nails-03']],
	[8, ['winter-01', 'winter-04', 'winter-02', 'winter-03', 'winter-05']],
	[9, ['gum-02', 'gum-01', 'gum-03', 'gum-04']],
	[10, ['kids-candy-01', 'kids-candy-02', 'kids-candy-03', 'kids-candy-04', 'kids-candy-05']],
	[11, ['reading-dark-02', 'reading-dark-01', 'reading-dark-03', 'reading-dark-04']],
	[12, ['balance-01', 'balance-02', 'balance-03', 'hand-01', 'winter-02']],
	[13, ['knuckles-03', 'knuckles-04', 'xray-hands-01', 'knuckles-01@8', 'xray-01', 'hand-01@5']],
	[14, ['brain-scan-01@10', 'carrot-03', 'kids-candy-05', 'knuckles-02@8']],
];
const key = (c: string) => c.replace('@', '_');
export const SHOTS: [string, number][] = PLAN.flatMap(([p, clips]) => {
	const a = at(p);
	const b = p < ABZ.length ? at(p + 1) : VOICE_SEC;
	return clips.map((c, i) => [key(c.includes('@') ? c : c + '@0'), a + ((b - a) * i) / clips.length] as [string, number]);
});

export const CHAPTERS = (
	[
		[3, '10% мозга'],
		[4, 'Карта вкусов'],
		[5, 'Морковка'],
		[6, 'Бритьё'],
		[7, 'Ногти после смерти'],
		[8, 'Тепло и шапка'],
		[9, 'Жвачка'],
		[10, 'Сахар'],
		[11, 'Чтение в темноте'],
		[12, 'Пять чувств'],
	] as [number, string][]
).map(([p, title]) => ({p, title, at: at(p) + 0.1}));

export const PLATES = [1, ABZ.length];

export const SHORTS: {id: string; from: number; to: number; title: string; outro?: string; ask?: string}[] = [{id: 'Short-unger', from: 222.24, to: 263.56, title: 'Хруст пальцев', outro: 'Полное видео - на канале', ask: 'Хрустишь пальцами? Признавайся'}, {id: 'Short-morkov', from: 68.40, to: 95.61, title: 'Морковка', outro: 'Полное видео - на канале', ask: 'В какой миф ты верил до этого видео?'}, {id: 'Short-yazyk', from: 37.68, to: 71.95, title: 'Карта вкусов', outro: 'Полное видео - на канале', ask: 'Тебе тоже это рассказывали в школе?'}, {id: 'Short-sahar', from: 160.84, to: 187.28, title: 'Сахар и дети', outro: 'Полное видео - на канале', ask: 'Согласен или нет? Пиши'}, {id: 'Short-brite', from: 92.06, to: 113.05, title: 'Бритьё', outro: 'Полное видео - на канале', ask: 'Верил в это? Да или нет?'}];

export const COVER = {clip: 'knuckles-01_0', sec: 3, small: '60 лет хрустел', big: 'одной рукой'};
