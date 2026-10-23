// Таймлайн ролика 03-ptitsy. Сгенерировано scripts/prepare.py - править plan.json, не этот файл.
import slova from './slova.json';
import abzacy from './abzacy.json';

export const FPS = 30;
export type Word = {w: string; s: number; e: number; p: number};
export const WORDS: Word[] = slova as Word[];
const ABZ = abzacy as {n: number; s: number; e: number}[];
export const VOICE_SEC = ABZ[ABZ.length - 1].e;
const at = (p: number) => ABZ[p - 1].s;

export const PLAN: [number, string[]][] = [
	[1, ['grass-fire-01', 'raptor-flying-02']],
	[2, ['cockatoo-01', 'crow-02', 'grey-parrot-01', 'budgie-02']],
	[3, ['cockatoo-02', 'trash-bins-01', 'cockatoo-03', 'trash-bins-02', 'cockatoo-04']],
	[4, ['cockatoo-01', 'cockatoo-05', 'cockatoo-06', 'cockatoo-01@6']],
	[5, ['crow-02', 'crow-04', 'crow-01', 'crow-06']],
	[6, ['crow-05', 'crow-07', 'crow-03', 'crow-08']],
	[7, ['raven-01', 'raven-03', 'raven-05', 'raven-04']],
	[8, ['pigeon-02', 'xray-01', 'pigeon-03', 'xray-02', 'pigeon-01']],
	[9, ['pigeon-04', 'pigeon-05', 'pigeon-01@15', 'pigeon-02@10']],
	[10, ['grey-parrot-01', 'grey-parrot-03', 'macaw-01', 'grey-parrot-02']],
	[11, ['budgie-01', 'budgie-02', 'budgie-04', 'budgie-03']],
	[12, ['heron-01', 'heron-02', 'heron-03', 'heron-02@60']],
	[13, ['kite-perched-01', 'grass-fire-02', 'raptor-flying-03', 'savanna-fire-01', 'grass-fire-03', 'raptor-flying-04', 'grass-fire-04']],
	[14, ['cockatoo-04', 'crow-04', 'heron-01@5', 'kite-perched-01@10']],
];
const key = (c: string) => c.replace('@', '_');
export const SHOTS: [string, number][] = PLAN.flatMap(([p, clips]) => {
	const a = at(p);
	const b = p < ABZ.length ? at(p + 1) : VOICE_SEC;
	return clips.map((c, i) => [key(c.includes('@') ? c : c + '@0'), a + ((b - a) * i) / clips.length] as [string, number]);
});

export const CHAPTERS = (
	[
		[3, 'Какаду и баки'],
		[4, 'Танцор Снежок'],
		[5, 'Вороны и опасность'],
		[6, 'Ворона считает'],
		[7, 'Ворон и завтра'],
		[8, 'Голуби-врачи'],
		[9, 'Голуби читают'],
		[10, 'Жако помогает'],
		[11, 'Попугайчики зевают'],
		[12, 'Цапля-рыбак'],
	] as [number, string][]
).map(([p, title]) => ({p, title, at: at(p) + 0.1}));

export const PLATES = [1, ABZ.length];

export const SHORTS: {id: string; from: number; to: number; title: string; outro?: string; ask?: string}[] = [{id: 'Short-podzhigateli', from: 236.04, to: 268.46, title: 'Птицы-поджигатели', outro: 'Полное видео - на канале', ask: 'Поверил бы, если бы не учёные?'}, {id: 'Short-kakadu', from: 21.93, to: 48.11, title: 'Какаду', outro: 'Полное видео - на канале', ask: 'Какие птицы хулиганят у тебя во дворе?'}, {id: 'Short-vorony', from: 66.77, to: 95.44, title: 'Вороны', outro: 'Полное видео - на канале', ask: 'Видел такое у себя во дворе?'}, {id: 'Short-schet', from: 91.89, to: 114.15, title: 'Ворона считает', outro: 'Полное видео - на канале', ask: 'Какая птица, по-твоему, самая умная?'}, {id: 'Short-golubi', from: 129.71, to: 156.72, title: 'Голуби', outro: 'Полное видео - на канале', ask: 'Доверил бы голубю свой снимок?'}];

export const COVER = {clip: 'kite-perched-01_0', sec: 3, small: 'Эти птицы', big: 'поджигают траву'};
