// Таймлайн ролика 02-zashchita. Сгенерировано scripts/prepare.py - править plan.json, не этот файл.
import slova from './slova.json';
import abzacy from './abzacy.json';

export const FPS = 30;
export type Word = {w: string; s: number; e: number; p: number};
export const WORDS: Word[] = slova as Word[];
const ABZ = abzacy as {n: number; s: number; e: number}[];
export const VOICE_SEC = ABZ[ABZ.length - 1].e;
const at = (p: number) => ABZ[p - 1].s;

export const PLAN: [number, string[]][] = [
	[1, ['termite-02', 'termite-01']],
	[2, ['hedgehog-03', 'octopus-02', 'pufferfish-02', 'zebra-01']],
	[3, ['hedgehog-01', 'hedgehog-02', 'hedgehog-04', 'hedgehog-05']],
	[4, ['porcupine-01', 'porcupine-02', 'porcupine-03', 'porcupine-02@10']],
	[5, ['stick-insect-01', 'stick-insect-02', 'stick-insect-03', 'stick-insect-01@11']],
	[6, ['caterpillar-01', 'caterpillar-02', 'caterpillar-03', 'caterpillar-04']],
	[7, ['octopus-01', 'octopus-02', 'octopus-03', 'octopus-04']],
	[8, ['pufferfish-01', 'pufferfish-02', 'pufferfish-03', 'pufferfish-04']],
	[9, ['sea-cucumber-01', 'sea-cucumber-02', 'sea-cucumber-03', 'sea-cucumber-04']],
	[10, ['zebra-01', 'zebra-02', 'horse-flymask-01', 'zebra-03', 'zebra-04']],
	[11, ['lizard-01', 'lizard-02', 'lizard-03', 'lizard-04']],
	[12, ['armadillo-01', 'armadillo-01@8', 'road-night-01', 'armadillo-01@4']],
	[13, ['termite-01', 'rainforest-01', 'termite-02', 'termite-nest-01', 'rainforest-02', 'termite-02@7']],
	[14, ['hedgehog-06', 'octopus-03', 'zebra-04', 'termite-02']],
];
const key = (c: string) => c.replace('@', '_');
export const SHOTS: [string, number][] = PLAN.flatMap(([p, clips]) => {
	const a = at(p);
	const b = p < ABZ.length ? at(p + 1) : VOICE_SEC;
	return clips.map((c, i) => [key(c.includes('@') ? c : c + '@0'), a + ((b - a) * i) / clips.length] as [string, number]);
});

export const CHAPTERS = (
	[
		[3, 'Ёж'],
		[4, 'Дикобраз'],
		[5, 'Палочник'],
		[6, 'Гусеница'],
		[7, 'Осьминог'],
		[8, 'Иглобрюх'],
		[9, 'Морской огурец'],
		[10, 'Зебра'],
		[11, 'Ящерица'],
		[12, 'Броненосец'],
	] as [number, string][]
).map(([p, title]) => ({p, title, at: at(p) + 0.1}));

export const PLATES = [1, ABZ.length];

export const SHORTS: {id: string; from: number; to: number; title: string; outro?: string; ask?: string}[] = [{id: 'Short-termit', from: 218.52, to: 260.11, title: 'Термит', outro: 'Полное видео - на канале', ask: 'Какая защита у зверей самая безумная?'}, {id: 'Short-ogurec', from: 140.36, to: 159.72, title: 'Морской огурец', outro: 'Полное видео - на канале', ask: 'Знал об этом раньше? Пиши да или нет'}, {id: 'Short-iglobryuh', from: 117.86, to: 143.91, title: 'Иглобрюх', outro: 'Полное видео - на канале', ask: 'Попробовал бы рыбу фугу?'}, {id: 'Short-zebra', from: 156.17, to: 185.22, title: 'Зебра', outro: 'Полное видео - на канале', ask: 'Зачем зебре полоски? Ты как думал?'}, {id: 'Short-dikobraz', from: 39.26, to: 62.34, title: 'Дикобраз', outro: 'Полное видео - на канале', ask: 'Тоже думал, что дикобраз стреляет иглами?'}];

export const COVER = {clip: 'termite-02_0', sec: 3, small: 'Этот термит', big: 'взрывается'};
