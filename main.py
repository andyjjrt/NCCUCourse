from tqdm import tqdm, trange
import CourseRate, TeacherId, MoodleId


pbar = trange(3)
pbar.set_postfix_str("processing: TeacherId")
TeacherId.main()
pbar.update(1)
pbar.set_postfix_str("processing: MoodleId")
MoodleId.main()
pbar.update(1)
pbar.set_postfix_str("processing: CourseRate")
CourseRate.main()
pbar.update(1)