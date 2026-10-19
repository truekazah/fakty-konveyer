// Общий монтаж роликов фактов (канал СХЕМА): длинный 16:9 и Shorts 9:16 из одного таймлайна.
// Что показывать и когда - в data.ts папки ролика; здесь только вид, звук и переходы.
// Время везде - секунды голоса (public/voice.wav), в кадры переводит F().
import React from 'react';
import {AbsoluteFill, Audio, Easing, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {loadFont} from '@remotion/fonts';
import * as D from './data';
import {CHAPTERS, FPS, PLATES, SHOTS, VOICE_SEC, WORDS, Word} from './data';
// FOCUS в data.ts (необязательно): {клип: 0-100} - куда сдвигать обрезку по ширине в Shorts, 50 - центр.
const FOCUS: Record<string, number> = (D as {FOCUS?: Record<string, number>}).FOCUS ?? {};

loadFont({family: 'Oswald', url: staticFile('fonts/Oswald.ttf'), weight: '200 700'});
const FONT = "'Oswald', sans-serif";
const YEL = '#FFD23F';
const INK = '#0b0b0d';
const F = (t: number) => Math.round(t * FPS);
const FADE = 6;
// Финальная заставка длинного ролика (сек): музыка, «Смотри дальше» сверху, середина свободна под элементы YouTube.
export const END_SEC = 12;

// ---------- кадр со стока: медленный наезд или отъезд ----------
const Shot: React.FC<{src: string; dur: number; i: number}> = ({src, dur, i}) => {
	const f = useCurrentFrame();
	const zin = i % 2 === 0;
	const kb = interpolate(f, [0, dur], zin ? [1.0, 1.08] : [1.08, 1.0]);
	const dx = interpolate(f, [0, dur], zin ? [0, -16] : [12, 0]);
	const op = i === 0 ? 1 : interpolate(f, [0, FADE], [0, 1], {extrapolateRight: 'clamp'});
	return (
		<AbsoluteFill style={{opacity: op}}>
			<AbsoluteFill style={{transform: `scale(${kb}) translateX(${dx}px)`}}>
				<OffthreadVideo
					src={staticFile(`stock/${src}.mp4`)}
					muted
					style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${FOCUS[src.replace(/_[\d.]+$/, '')] ?? 50}% 50%`}}
				/>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

// ---------- субтитры: группы по смыслу, текущее слово жёлтое ----------
const groups = (max: number) => {
	const out: {from: number; to: number; words: Word[]}[] = [];
	let cur: Word[] = [];
	const push = () => {
		if (cur.length) out.push({from: F(cur[0].s), to: F(cur[cur.length - 1].e + 0.25), words: cur});
		cur = [];
	};
	WORDS.forEach((w, k) => {
		const next = WORDS[k + 1];
		if (cur.length && cur[0].p !== w.p) push();
		cur.push(w);
		const len = cur.map((x) => x.w).join(' ').length;
		const stop = /[.!?:;]$/.test(w.w) || (/,$/.test(w.w) && len > max * 0.45) || len > max;
		if (stop || !next || (next && next.s - w.e > 0.6)) push();
	});
	for (let k = 0; k < out.length - 1; k++) out[k].to = Math.min(out[k].to, out[k + 1].from);
	return out;
};
const G_H = groups(42);
const G_V = groups(24);
const inPlate = (p: number) => PLATES.includes(p);

const Karaoke: React.FC<{vertical: boolean; plateFirst?: number}> = ({vertical, plateFirst}) => {
	const f = useCurrentFrame();
	const G = vertical ? G_V : G_H;
	const g = G.find((x) => f >= x.from && f < x.to);
	if (!g) return null;
	const p = g.words[0].p;
	const plate = inPlate(p) || (plateFirst !== undefined && g.from < plateFirst);
	const since = f - g.from;
	const pop = interpolate(since, [0, 4], [0.88, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.back(2))});
	const t = f / FPS;
	const size = plate ? (vertical ? 96 : 80) : vertical ? 88 : 62;
	// обычная div, а не AbsoluteFill: у AbsoluteFill колонка, и субтитр уезжал в центр и не переносился
	const box: React.CSSProperties = {position: 'absolute', left: vertical ? 60 : 160, right: vertical ? 60 : 160, display: 'flex', flexDirection: 'row', justifyContent: 'center'};
	const pos: React.CSSProperties = plate
		? {top: 0, bottom: 0, alignItems: 'center'}
		: vertical
			? {top: 1130, alignItems: 'flex-start'}
			: {bottom: 60, alignItems: 'flex-end'};
	return (
		<div style={{...box, ...pos}}>
			<div
				style={{
					display: 'flex',
					flexWrap: 'wrap',
					justifyContent: 'center',
					gap: `0 ${Math.round(size * 0.3)}px`,
					padding: plate ? '24px 40px' : 0,
					borderRadius: 18,
					background: plate ? YEL : 'transparent',
					boxShadow: plate ? '0 18px 50px rgba(0,0,0,.45)' : 'none',
					transform: `scale(${pop})`,
					maxWidth: plate && !vertical ? 1300 : '100%',
				}}
			>
				{g.words.map((w, i) => {
					const said = t >= w.s;
					const now = t >= w.s && t < w.e + 0.05;
					const k = now ? interpolate(t - w.s, [0, 0.08, 0.2], [1, 1.07, 1.03], {extrapolateRight: 'clamp'}) : 1;
					return (
						<span
							key={i}
							style={
								plate
									? {font: `700 ${size}px/1.15 ${FONT}`, textTransform: 'uppercase', color: INK, opacity: said ? 1 : 0.35, display: 'inline-block', transform: `scale(${k})`}
									: {
											font: `700 ${size}px/1.2 ${FONT}`,
											textTransform: 'uppercase',
											color: now ? YEL : '#ffffff',
											WebkitTextStroke: `${Math.round(size / 7)}px ${INK}`,
											paintOrder: 'stroke fill',
											textShadow: '0 5px 16px rgba(0,0,0,.6)',
											display: 'inline-block',
											transform: `scale(${k})`,
									  }
							}
						>
							{w.w}
						</span>
					);
				})}
			</div>
		</div>
	);
};

// ---------- название главы: выезжает слева на 3 секунды ----------
const Chapter: React.FC<{n: number; title: string}> = ({n, title}) => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	const p = spring({frame: f, fps, config: {damping: 16, stiffness: 120}});
	const out = interpolate(f, [F(3.2), F(3.6)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const x = interpolate(p, [0, 1], [-520, 0]) - out * 520;
	return (
		<AbsoluteFill>
			<div style={{position: 'absolute', left: 90, top: 80, transform: `translateX(${x}px)`, display: 'flex', alignItems: 'stretch'}}>
				<div style={{background: YEL, color: INK, font: `700 46px/1 ${FONT}`, padding: '18px 22px', display: 'flex', alignItems: 'center'}}>{n}</div>
				<div style={{background: 'rgba(11,11,13,.82)', color: '#fff', font: `700 64px/1 ${FONT}`, textTransform: 'uppercase', padding: '16px 30px', letterSpacing: 1}}>
					{title}
				</div>
			</div>
		</AbsoluteFill>
	);
};

// Затемнение снизу под субтитры (и сверху в вертикали - под заголовок).
const Shade: React.FC<{vertical: boolean}> = ({vertical}) => (
	<AbsoluteFill
		style={{
			background: vertical
				? 'linear-gradient(to bottom, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 50%, rgba(0,0,0,.5) 68%, rgba(0,0,0,.3) 100%)'
				: 'linear-gradient(to bottom, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 62%, rgba(0,0,0,.6) 100%)',
		}}
	/>
);

// ---------- музыка: петля, тише под голосом ----------
const MUSIC_SEC = 118.0; // длина public/sfx/music.mp3; другой трек - поменять
const duck = (() => {
	const n = F(VOICE_SEC + END_SEC + 6);
	const talk = new Array(n).fill(false);
	for (const w of WORDS) for (let f = F(w.s - 0.1); f <= F(w.e + 0.25); f++) if (f >= 0 && f < n) talk[f] = true;
	const out: number[] = [];
	let v = 0.03;
	for (let f = 0; f < n; f++) {
		const target = talk[f] ? 0.035 : 0.07;
		v += (target - v) * (target < v ? 0.3 : 0.06);
		out.push(v);
	}
	return out;
})();
const Music: React.FC<{off: number; len: number}> = ({off, len}) => {
	const ml = F(MUSIC_SEC);
	const step = ml - 90; // перекрытие 3 сек между повторами
	const reps = Math.ceil(len / step) + 1;
	return (
		<>
			{Array.from({length: reps}, (_, r) => (
				<Sequence key={r} from={r * step} durationInFrames={ml}>
					<Audio
						src={staticFile('sfx/music.mp3')}
						volume={(f) => {
							const abs = r * step + f;
							const xin = r === 0 ? 1 : interpolate(f, [0, 90], [0, 1], {extrapolateRight: 'clamp'});
							const xout = interpolate(f, [ml - 90, ml], [1, 0], {extrapolateLeft: 'clamp'});
							const end = interpolate(abs, [len - 45, len], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
							return duck[Math.min(abs + off, duck.length - 1)] * xin * xout * end;
						}}
					/>
				</Sequence>
			))}
		</>
	);
};

// ---------- весь таймлайн; off - с какой секунды голоса начинать (для Shorts) ----------
// outro - плашка в конце Short; пустая строка - без плашки (Short сам по себе, длинной версии нет).
// ask - вопрос зрителю крупно над outro, плашка висит дольше (3,8 сек), чтобы успели прочитать.
export const Film: React.FC<{from?: number; to?: number; title?: string; vertical?: boolean; outro?: string; ask?: string}> = ({from = 0, to, title, vertical = false, outro = 'Полное видео - на канале', ask}) => {
	const tail = vertical && outro ? F(ask ? 3.8 : 1.8) : 0;
	const off = F(from);
	const endcard = vertical ? 0 : F(END_SEC);
	const end = F(to ?? VOICE_SEC + 1.5) + endcard;
	const len = end - off;
	const shots = SHOTS.map(([src, s], i) => ({src, a: F(s), b: i + 1 < SHOTS.length ? F(SHOTS[i + 1][1]) : F(VOICE_SEC + 3 + END_SEC)}))
		.filter((s) => s.b > off && s.a < end);
	return (
		<AbsoluteFill style={{background: INK}}>
			<Sequence from={-off}>
				{shots.map((s, i) => (
					<Sequence key={s.a} from={Math.max(s.a, off) - (i === 0 ? 0 : FADE)} durationInFrames={s.b - Math.max(s.a, off) + (i === 0 ? 0 : FADE) + 2}>
						<Shot src={s.src} dur={s.b - s.a + FADE} i={i} />
					</Sequence>
				))}
				<Shade vertical={vertical} />
				{!vertical &&
					CHAPTERS.map((c, i) => (
						<Sequence key={c.p} from={F(c.at)} durationInFrames={F(3.7)}>
							<Chapter n={i + 1} title={c.title} />
						</Sequence>
					))}
				{/* в Shorts последние 1,8 сек (с вопросом 3,8) - плашка «Полное видео», голос и субтитры к этому моменту уже кончились */}
				<Sequence durationInFrames={tail ? end - tail : undefined}>
					<Karaoke vertical={vertical} plateFirst={vertical ? F(from) + F(2.2) : undefined} />
				</Sequence>
				<Audio src={staticFile('voice.wav')} volume={(f) => (tail && f > end - tail ? 0 : 1)} />
			</Sequence>
			{vertical && title ? (
				<AbsoluteFill style={{alignItems: 'center'}}>
					<div style={{marginTop: 220, background: YEL, color: INK, font: `700 92px/1 ${FONT}`, textTransform: 'uppercase', padding: '16px 34px'}}>{title}</div>
				</AbsoluteFill>
			) : null}
			{tail ? (
				<Sequence from={len - tail}>
					<AbsoluteFill style={{background: 'rgba(0,0,0,.6)', alignItems: 'center', justifyContent: 'center'}}>
						{ask ? (
							<>
								<div style={{background: YEL, color: INK, font: `700 80px/1.15 ${FONT}`, textTransform: 'uppercase', padding: '32px 44px', textAlign: 'center', margin: '0 60px'}}>
									{ask}
								</div>
								<div style={{marginTop: 48, background: '#fff', color: INK, font: `700 52px/1.15 ${FONT}`, textTransform: 'uppercase', padding: '18px 32px', textAlign: 'center'}}>
									{outro}
								</div>
							</>
						) : (
							<div style={{background: YEL, color: INK, font: `700 74px/1.15 ${FONT}`, textTransform: 'uppercase', padding: '28px 40px', textAlign: 'center', margin: '0 70px'}}>
								{outro}
							</div>
						)}
					</AbsoluteFill>
				</Sequence>
			) : null}
			{vertical && outro === '' ? (
				<Sequence from={len - F(1.4)}>
					<SubPlate />
				</Sequence>
			) : null}
			{endcard ? (
				<Sequence from={len - endcard}>
					<EndCard />
				</Sequence>
			) : null}
			<Music off={off} len={len} />
		</AbsoluteFill>
	);
};

// ---------- конец Short: после последнего слова - крупная плашка «Подпишись», ролик не обрывается на полуслове ----------
const SubPlate: React.FC = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	const p = spring({frame: f, fps, config: {damping: 12, stiffness: 160}});
	return (
		<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', background: `rgba(0,0,0,${interpolate(f, [0, 8], [0, 0.45], {extrapolateRight: 'clamp'})})`}}>
			<div style={{background: YEL, color: INK, font: `700 120px/1 ${FONT}`, textTransform: 'uppercase', padding: '26px 48px', borderRadius: 18, transform: `scale(${interpolate(p, [0, 1], [0.6, 1])})`, boxShadow: '0 18px 50px rgba(0,0,0,.45)'}}>
				Подпишись
			</div>
		</AbsoluteFill>
	);
};

// ---------- финальная заставка длинного ролика ----------
const EndCard: React.FC = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	const op = interpolate(f, [0, 12], [0, 1], {extrapolateRight: 'clamp'});
	const p = spring({frame: f - 6, fps, config: {damping: 14, stiffness: 120}});
	return (
		<AbsoluteFill style={{background: `rgba(0,0,0,${0.62 * op})`, alignItems: 'center'}}>
			<div style={{marginTop: 70, transform: `scale(${interpolate(p, [0, 1], [0.8, 1])})`, opacity: op, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
				<div style={{background: YEL, color: INK, font: `700 84px/1 ${FONT}`, textTransform: 'uppercase', padding: '18px 40px'}}>Смотри дальше</div>
				<div style={{marginTop: 18, color: '#fff', font: `700 44px/1 ${FONT}`, textTransform: 'uppercase', letterSpacing: 2}}>Да ну, правда?!</div>
			</div>
		</AbsoluteFill>
	);
};

// ---------- обложка YouTube 1280x720: кадр со стока + крупный текст ----------
export const Cover: React.FC<{clip: string; sec: number; small: string; big: string; right?: boolean}> = ({clip, sec, small, big, right}) => (
	<AbsoluteFill style={{background: INK}}>
		<OffthreadVideo src={staticFile(`stock/${clip}.mp4`)} startFrom={Math.round(sec * FPS)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
		<AbsoluteFill style={{background: `linear-gradient(to ${right ? 'left' : 'right'}, rgba(0,0,0,.78) 0%, rgba(0,0,0,.35) 55%, rgba(0,0,0,0) 80%)`}} />
		<AbsoluteFill style={{justifyContent: 'center', alignItems: right ? 'flex-end' : 'flex-start', padding: '0 60px'}}>
			<div style={{font: `700 58px/1.05 ${FONT}`, color: '#fff', textTransform: 'uppercase', WebkitTextStroke: `8px ${INK}`, paintOrder: 'stroke fill'}}>{small}</div>
			<div style={{marginTop: 14, background: YEL, color: INK, font: `700 112px/1 ${FONT}`, textTransform: 'uppercase', padding: '12px 26px', transform: 'rotate(-2deg)'}}>
				{big}
			</div>
		</AbsoluteFill>
	</AbsoluteFill>
);
