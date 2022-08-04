from tqdm import tqdm, trange
import CourseRate, TeacherId, MoodleId, CourseResult


pbar = trange(4)
pbar.set_postfix_str("processing: TeacherId")
TeacherId.main()
pbar.update(1)
pbar.set_postfix_str("processing: MoodleId")
MoodleId.main()
pbar.update(1)
pbar.set_postfix_str("processing: CourseRate")
CourseRate.main()
pbar.update(1)
pbar.set_postfix_str("processing: CourseRaesult")
CourseResult.main()
pbar.update(1)