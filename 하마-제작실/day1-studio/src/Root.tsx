import {
  Day1V2Reel,
  Day1V2Mini,
  Day1V2Save,
  Day1V2Morning,
  Day1V2Night,
} from "./Day1V2";
import { PhotoCover } from "./PhotoCover";
import { Composition, Still } from "remotion";
import { Day1Reel, Mini, Morning, Night, SaveCard } from "./Day1";
export const RemotionRoot = () => (
  <>
    <Composition
      id="Day1-V2-Reel"
      component={Day1V2Reel}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={900}
    />
    <Still
      id="Day1-V2-Mini"
      component={Day1V2Mini}
      width={1080}
      height={1350}
    />
    <Still
      id="Day1-V2-Save"
      component={Day1V2Save}
      width={1080}
      height={1350}
    />
    <Still
      id="Day1-V2-Morning-1"
      component={Day1V2Morning}
      width={1080}
      height={1920}
      defaultProps={{ page: 1 }}
    />
    <Still
      id="Day1-V2-Morning-2"
      component={Day1V2Morning}
      width={1080}
      height={1920}
      defaultProps={{ page: 2 }}
    />
    <Still
      id="Day1-V2-Morning-3"
      component={Day1V2Morning}
      width={1080}
      height={1920}
      defaultProps={{ page: 3 }}
    />
    <Still
      id="Day1-V2-Night-1"
      component={Day1V2Night}
      width={1080}
      height={1920}
      defaultProps={{ page: 1 }}
    />
    <Still
      id="Day1-V2-Night-2"
      component={Day1V2Night}
      width={1080}
      height={1920}
      defaultProps={{ page: 2 }}
    />

    <Still
      id="Photo-Collage-Cover"
      component={PhotoCover}
      width={1080}
      height={1350}
    />
    <Composition
      id="Day1-Reel"
      component={Day1Reel}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
    <Still id="Day1-Mini" component={Mini} width={1080} height={1350} />
    <Still id="Day1-Save" component={SaveCard} width={1080} height={1350} />
    <Still
      id="Morning-1"
      component={Morning}
      width={1080}
      height={1920}
      defaultProps={{ page: 1 }}
    />
    <Still
      id="Morning-2"
      component={Morning}
      width={1080}
      height={1920}
      defaultProps={{ page: 2 }}
    />
    <Still
      id="Night-1"
      component={Night}
      width={1080}
      height={1920}
      defaultProps={{ page: 1 }}
    />
    <Still
      id="Night-2"
      component={Night}
      width={1080}
      height={1920}
      defaultProps={{ page: 2 }}
    />
  </>
);
