// Композиции: Rolik - длинный 16:9, Short-* - вертикальные куски того же таймлайна (список в data.ts).
import React from 'react';
import {Composition, Still} from 'remotion';
import {Cover, END_SEC, Film} from './Film';
import {COVER, FPS, SHORTS, VOICE_SEC} from './data';

export const Root: React.FC = () => (
	<>
		<Composition id="Rolik" component={Film} durationInFrames={Math.round((VOICE_SEC + 1.5 + END_SEC) * FPS)} fps={FPS} width={1920} height={1080} defaultProps={{}} />
		<Still id="Oblozhka" component={Cover} width={1280} height={720} defaultProps={COVER} />
		{SHORTS.map((s) => (
			<Composition
				key={s.id}
				id={s.id}
				component={Film}
				durationInFrames={Math.round((s.to - s.from) * FPS)}
				fps={FPS}
				width={1080}
				height={1920}
				defaultProps={{from: s.from, to: s.to, title: s.title, vertical: true, outro: s.outro}}
			/>
		))}
	</>
);
