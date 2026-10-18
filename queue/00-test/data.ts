// Таймлайн ролика 00-test. Сгенерировано scripts/prepare.py - править plan.json, не этот файл.
import slova from './slova.json';
import abzacy from './abzacy.json';

export const FPS = 30;
export type Word = {w: string; s: number; e: number; p: number};
export const WORDS: Word[] = slova as Word[];
const ABZ = abzacy as {n: number; s: number; e: number}[];
export const VOICE_SEC = ABZ[ABZ.length - 1].e;
const at = (p: number) => ABZ[p - 1].s;

export const PLAN: [number, string[]][] = [
	[1, ['greenland-shark-01@64']],
	[2, ['giant-tortoise-01', 'ancient-tree-03', 'elephant-family-01']],
	[3, ['giant-tortoise-01@8', 'giant-tortoise-02', 'giant-tortoise-03', 'giant-tortoise-01@16']],
	[4, ['cockatoo-01', 'cockatoo-03', 'cockatoo-02']],
	[5, ['elephant-family-01@8', 'elephant-family-03', 'elephant-family-02', 'elephant-family-01@16']],
	[6, ['bowhead-whale-02', 'bowhead-whale-03']],
	[7, ['clam-shell-03', 'clam-shell-02', 'clam-shell-01']],
	[8, ['bristlecone-pine-03', 'ancient-tree-02', 'ancient-tree-03@8', 'bristlecone-pine-01']],
	[9, ['plankton-03', 'jellyfish-underwater-02', 'deep-sea-creatures-02']],
	[10, ['sponge-underwater-01', 'sponge-underwater-03', 'sponge-underwater-02']],
	[11, ['old-woman-portrait-01', 'old-woman-portrait-03', 'old-woman-portrait-02']],
	[12, ['arctic-ice-ocean-01@4', 'greenland-shark-01@13', 'arctic-ice-ocean-02@10', 'greenland-shark-01@92']],
	[13, ['laboratory-scientist-01', 'greenland-shark-01@80']],
	[14, ['giant-tortoise-02@8', 'bristlecone-pine-01@30']],
];
const key = (c: string) => c.replace('@', '_');
export const SHOTS: [string, number][] = PLAN.flatMap(([p, clips]) => {
	const a = at(p);
	const b = p < ABZ.length ? at(p + 1) : VOICE_SEC;
	return clips.map((c, i) => [key(c.includes('@') ? c : c + '@0'), a + ((b - a) * i) / clips.length] as [string, number]);
});

export const CHAPTERS = (
	[
		[3, 'Черепаха Джонатан'],
		[4, 'Попугаи'],
		[5, 'Слоны'],
		[6, 'Гренландский кит'],
		[7, 'Моллюск Минг'],
		[8, 'Деревья'],
		[9, 'Медуза'],
		[10, 'Губки'],
		[11, 'Люди'],
		[12, 'Гренландская акула'],
	] as [number, string][]
).map(([p, title]) => ({p, title, at: at(p) + 0.1}));

export const PLATES = [1, ABZ.length];

export const SHORTS: {id: string; from: number; to: number; title: string; outro?: string}[] = [{id: 'Short-minq', from: 85.61, to: 106.03, title: 'Моллюск Минг', outro: 'Полное видео - на канале'}, {id: 'Short-akula', from: 166.19, to: 207.90, title: 'Гренландская акула', outro: 'Полное видео - на канале'}];

export const COVER = {clip: 'greenland-shark-01_60', sec: 1, small: 'Этой акуле', big: '400 лет'};
