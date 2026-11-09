import {AbsoluteFill} from "remotion";
import cover from "./photo-cover.json";
export const PhotoCover = () => <AbsoluteFill><style>{cover.css}</style><div dangerouslySetInnerHTML={{__html:cover.markup}}/></AbsoluteFill>;
